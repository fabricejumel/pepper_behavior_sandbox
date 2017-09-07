import smach
import rospy


class SpeechAnalyser(smach.State):
    def __init__(self, controller, wait=10):
        self.question = ['Pepper, wie geht es Dir?',
                         'Pepper, woher kommst Du?',
                         'Pepper, was kannst Du alles tun?',
                         'Pepper, was kann ich auf der itelligence World alles sehen?','']
        self.wait = wait
        self.controller = controller
        smach.State.__init__(self, outcomes=['success', 'no_cmd'], output_keys=['msg_output'])

    def execute(self, userdata):
        self.controller.clean()
        userdata.msg_output = None
        for i in range(0, self.wait):
            cmd = self.controller.getCmd()
            rospy.sleep(1)
            if cmd:
                print('Got msg %s' %cmd)
                for i in self.question:
                    if cmd == self.question[i]:
                        userdata.msg_output = i
                        return 'success'
        print('No cmd.')
        return 'noc_cmd'