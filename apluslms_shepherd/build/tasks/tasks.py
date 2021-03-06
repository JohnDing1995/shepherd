import os
import shutil

from apluslms_shepherd.build.tasks import build_observer
from apluslms_shepherd.build.tasks.signals import task_step_mapping
from apluslms_shepherd.build.tasks.utils import bare_clone, get_current_build_number_list, roman_build, slugify

try:
    from subprocess import DEVNULL  # Python 3
except ImportError:
    DEVNULL = open(os.devnull, 'r+b', 0)

from celery.result import AsyncResult
from celery.utils.log import get_task_logger

from apluslms_shepherd.build.models import BuildState
from apluslms_shepherd.courses.models import CourseInstance
from apluslms_shepherd.extensions import celery
from apluslms_shepherd.config import DevelopmentConfig

logger = get_task_logger(__name__)


@celery.task
def update_state(course_id, build_number, state, action, log):
    """
    Take the updated state to MQ, this task is not going to the worker
    """
    logger.info("Sending state to frontend")


@celery.task
def pull_repo(base_path, url, branch, course_key, instance_key, build_number):
    """
    Clone bear repo to local, or update local one, generate working tree.
    """
    build_observer.enter_prepare()
    logger.info('url:%s, branch:%s course_key:%s instance_key:%s', url, branch, course_key, instance_key)
    logger.info("Pulling from %s", url)
    args = [base_path, url, course_key, instance_key, branch, build_number,
            os.path.join(DevelopmentConfig.REPO_KEYS_PATH, slugify(url), 'private.pem'), build_observer]
    return_code = bare_clone(*args)
    return {'code': return_code, 'msg': ''}


@celery.task
def build_repo(pull_result, base_path, course_key, instance_key, build_number):
    """
    build the course material with roman
    """
    logger.info("pull_repo result: %s", str(pull_result))
    build_observer.enter_build()
    # Check the result of last step
    if not pull_result['code'] == 0:
        logger.error('The clone task was failed, aborting the build task')
        return {'code': -1, 'msg': 'The clone task was failed, aborting the build task.'}
    log = "The repo has been pulled, Building the course, course key:{}, branch:{}\n".format(course_key, instance_key)
    logger.info(log)
    ins = CourseInstance.query.filter_by(course_key=course_key, instance_key=instance_key).first()
    build_observer.state_update(ins.id, build_number, task_step_mapping['build_repo'], BuildState.RUNNING,
                                log)
    number_list = get_current_build_number_list()
    log = "Current build task number of this instance in the queue:{}\n".format(number_list)
    logger.info(log)
    build_observer.state_update(ins.id, build_number, task_step_mapping['build_repo'], BuildState.RUNNING,
                                log)
    try:
        if int(build_number) < max(number_list):
            logger.warning(
                "Already have newer version in the task queue, task with build number %s aborted.", build_number)
            return {'code': 5, 'msg': "Already have newer version in the task queue, task with build number {} "
                                      "aborted.".format(build_number)}
    except (ValueError, TypeError):
        logger.error("Cannot compare current  build number with max number in the queue")
    code = roman_build(base_path, ins.id, course_key, instance_key, build_number)
    return {'code': code, 'msg': ''}


@celery.task
def deploy(build_result, deploy_base_path, base_path, course_key, instance_key, build_number):
    """
    Copy the build filed to deploy folder
    TODO: Support remote deploy location(Cloud .etc)
    """
    # Check the last step
    logger.info("build_repo result %s", build_result)
    if not build_result['code'] == 0:
        logger.error('The build task was failed, aborting the deployment task')
        return {'code': -1, 'msg': 'The clone task was failed or aborted, aborting the build task'}
    # Check is there has a newer version in the queue.If true, cancel the task and start cleaning
    number_list = get_current_build_number_list()
    if int(build_number) < max(number_list):
        logger.warning("Already have newer version in the task queue, task with build number %s aborted.", build_number)
        return {'code': 5,
                'msg': "Newer version in the task queue, task with build number {} aborted. Cleaning the local "
                       "repo".format(build_number)}
    logger.info(
        "The repo has been build, deploying the course, course key: %s, branch: %s", course_key, instance_key)
    try:
        build_path = os.path.join(base_path, 'builds', course_key, instance_key, build_number, "_build")
        deploy_path = os.path.join(deploy_base_path, course_key, instance_key, build_number)
        shutil.move(build_path, deploy_path)
    except (FileNotFoundError, OSError, IOError) as why:
        logger.error('Error: %', why.strerror)
        return {'code': 1, 'msg': 'Error when deploying files'}
    return {'code': 0, 'msg': 'successfully moved to deployment folder.'}


@celery.task
def clean(res, base_path, course_key, instance_key, build_number):
    """
    Clean the generated working tree.
    """
    logger.warning('Cleaning repo')
    path = os.path.join(base_path, 'builds', course_key, instance_key, build_number)
    try:
        logger.warning("Local work tree of build number %s deleted", build_number)
        build_observer.done()
        shutil.rmtree(path)
        return {'code': 0, 'msg': 'Worktree cleaned.'}
    except (FileNotFoundError, IOError, OSError) as why:
        logger.info('Error: %s', why.strerror)
        return {'code': 1, 'msg': 'Error when cleaning local worktree files,'}


@celery.task
def error_handler(uuid):
    result = AsyncResult(uuid)
    exc = result.get(propagate=False)
    logger.warning('Task %s raised exception: %s\n%s', uuid, exc, result.traceback)
