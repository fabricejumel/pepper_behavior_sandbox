#!/usr/bin/env python
from flexbe_core import EventState, Logger
from flexbe_core.proxy import ProxyActionClient
from actionlib_msgs.msg import GoalStatus
from naoqi_bridge_msgs.msg import SpeechWithFeedbackAction, SpeechWithFeedbackGoal

"""

"""


class TalkState(EventState):
    """
    Makes the Robot talk

    -- blocking             bool        Whether or not this state blocks execution
    -- message              String      What to say

    <= done                     Execution succeeded
    <= failed                   Execution failed
    """

    def __init__(self, message, blocking=True):
        """Constructor"""

        super(TalkState, self).__init__(outcomes=['done', 'failed'])

        self._blocking = blocking
        self._text = message
        self._action_topic = '/naoqi_tts_feedback'
        self._client = ProxyActionClient({self._action_topic: SpeechWithFeedbackAction})

        self._done = False
        self._failed = False

    def execute(self, userdata):
        """Wait for action result and return outcome accordingly"""

        if self._done:
            return 'done'
        if self._failed:
            return 'failed'

        if not self._blocking:
            return 'done'

        if self._client.has_result(self._action_topic):
            status = self._client.get_state(self._action_topic)
            if status == GoalStatus.SUCCEEDED:
                self._done = True
                Logger.loginfo('done')
                return 'done'
            elif status in [GoalStatus.PREEMPTED, GoalStatus.REJECTED,
                            GoalStatus.RECALLED, GoalStatus.ABORTED]:
                Logger.logwarn('TTS failed: %s' % str(status))
                self._failed = True
                return 'failed'

    def on_enter(self, userdata):
        """Create and send action goal"""

        self._done = False
        self._failed = False

        # Create and populate action goal
        goal = SpeechWithFeedbackGoal()
        goal.say = self._text

        try:
            self._client.send_goal(self._action_topic, goal)
            Logger.loginfo('Send TTS goal')
        except Exception as e:
            Logger.logwarn("Unable to send tts action goal:\n%s" % str(e))
            self._failed = True

    def cancel_active_goals(self):
        if self._client.is_available(self._action_topic):
            if self._client.is_active(self._action_topic):
                if not self._client.has_result(self._action_topic):
                    self._client.cancel(self._action_topic)
                    Logger.loginfo('Cancelled TTS active action goal.')

    def on_exit(self, userdata):
        if self._blocking:
            self.cancel_active_goals()

    def on_stop(self):
        if self._blocking:
            self.cancel_active_goals()
