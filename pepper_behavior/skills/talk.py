import rospy
import smach


class Talk(smach.State):
    def __init__(self, controller, text=None):
        self.text = text
        if self.text:
            input_k = []
        else:
            input_k = ['text']
        smach.State.__init__(self, outcomes=['success'], input_keys=input_k)
        self.talk = controller

    def execute(self, userdata):
        if self.text:
            talk = self.text
        else:
            talk = userdata.text
        result = self.talk.say_something(talk)
        return result