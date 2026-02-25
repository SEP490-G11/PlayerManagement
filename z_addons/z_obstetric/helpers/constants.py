class AppointmentState:
    NOT_YET_ARRIVED = "1"
    WAITING = "2"
    EXAMINING = "3"
    WAITING_FOR_ULTRASOUND = "4"
    RESULT_SA = "5"
    RESULT_TEST = "6"
    WAITING_FOR_CONCLUDE = "7"
    CONCLUDED_REGISTER_TIP = "8"
    FINISHED = "9"
    WAITING_FOR_TIP = "10"
    DOING_TIP = "11"
    FINISHED_TIP = "12"

APPOINTMENT_STATE_VALUES = set(
    getattr(AppointmentState, attr)
    for attr in dir(AppointmentState)
    if not attr.startswith("_")
)

APPOINTMENT_STATE_CHOICES = [
    (AppointmentState.NOT_YET_ARRIVED, "Not yet arrived"),
    (AppointmentState.WAITING, "Waiting"),
    (AppointmentState.EXAMINING, "Examining"),
    (AppointmentState.WAITING_FOR_ULTRASOUND, "Waiting for ultrasound"),
    (AppointmentState.RESULT_SA, "Result SA"),
    (AppointmentState.RESULT_TEST, "Result test"),
    (AppointmentState.WAITING_FOR_CONCLUDE, "Waiting for conclude"),
    (AppointmentState.CONCLUDED_REGISTER_TIP, "Concluded and register tip"),
    (AppointmentState.FINISHED, "Finished"),
    (AppointmentState.WAITING_FOR_TIP, "Waiting for tip"),
    (AppointmentState.DOING_TIP, "Doing tip"),
    (AppointmentState.FINISHED_TIP, "Finished tip"),
]

VISIT_STATE_LIST = [
    AppointmentState.EXAMINING,
    AppointmentState.FINISHED,
    AppointmentState.WAITING_FOR_ULTRASOUND,
    AppointmentState.RESULT_SA,
    AppointmentState.RESULT_TEST,
    AppointmentState.WAITING_FOR_CONCLUDE,
    AppointmentState.CONCLUDED_REGISTER_TIP,
    AppointmentState.WAITING_FOR_TIP,
    AppointmentState.DOING_TIP,
    AppointmentState.FINISHED_TIP,
]