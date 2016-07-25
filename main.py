from pete import Runner
from pete.examples import StringBroadcaster
from get_flag import FlagTask, FlagBroadcaster
from config import FLAG_TIMEOUT, RUNNER_TIMEOUT


def run():
    runner = Runner(
        tasks=[FlagTask(FLAG_TIMEOUT)],
        broadcasters=[FlagBroadcaster()],
        timeout=RUNNER_TIMEOUT
    )
    runner.main()

if __name__ == '__main__':
    run()
