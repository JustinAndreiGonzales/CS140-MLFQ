from model import MLFQ
from controller import Controller
from view import View


view = View()
inputs = view.get_input()
model = MLFQ(inputs.Q1, inputs.Q2, inputs.CS)
controller = Controller(model, view)
controller.run()

