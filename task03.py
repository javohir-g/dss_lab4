# Lab 4A. Task 3 - From the product owner's message to CRC cards (on paper)
# Student: Javohir Gayratov
#
# 3.1 Question: Underline the nouns and the verbs. Put every noun into one group: class,
#     attribute, actor, event with data, or vague word you must ask about (slide 7).
#     Answer: Nouns: patient, appointment, dentist, procedure, treatment room, working hours,
#     name, duration, price, 24 hours, fee, 50 000 sum, receptionist, system, SMS reminder,
#     evening. Verbs: books, works, has, can be moved, starts, is charged, confirms, sends.
#     Groups:
#     - class: patient (also an actor, the person who books), dentist, procedure
#     - event with data (class): appointment - it joins patient, dentist, procedure and time
#     - event with data: SMS reminder - to whom, the text, when it was sent
#     - attribute: treatment room and working hours (of Dentist); name, duration and price (of
#       Procedure); 24 hours and the 50 000 sum fee (constants of the move rule in Appointment)
#     - actor: receptionist (a person who uses the system, see 3.4)
#     - vague words: "system" (the whole program, not a class - which part sends the SMS?) and
#       "evening" (at what time exactly, and in which time zone?)
#     Questions to the product owner:
#     - "The evening before" - at what time exactly? What if the visit is booked after that time?
#     - "Moved" - only to another time, or also to another dentist?
#     - Are the 24 hours counted from the old start time of the visit?
#     - Can two dentists share one treatment room in different shifts?
#     - What happens to an appointment that the receptionist does not confirm?
#     The verbs give the responsibilities: books -> Schedule.book(), can be moved and is
#     charged -> Appointment.move_fee(), confirms -> Appointment.confirm(), sends ->
#     ReminderService.
#
# 3.2 Question: Write 4-6 CRC cards (slide 10): 2-4 responsibilities and the collaborators on
#     each card.
#     Answer: 6 cards (class | responsibilities | collaborators):
#     - Appointment | know the patient, dentist, procedure, start time and status; know its end
#       time (start + duration) and say if it overlaps another appointment; calculate the move
#       fee (0 until 24 hours before, then 50 000 sum); confirm, move to a new time |
#       Patient, Dentist, Procedure
#     - Schedule | keep all appointments, grouped by dentist; book a new appointment (checks the
#       working hours and that the time is free); move an appointment with the same checks and
#       take the fee; give the appointments of one day (for the reminders) | Appointment, Dentist
#     - Dentist | know the name, the treatment room and the working hours; say if a time is
#       inside the working hours | -
#     - Procedure | know the name and the price; know the duration (for the end time of an
#       appointment) | -
#     - Patient | know the name; know the phone number for the reminders | -
#     - ReminderService | every evening take tomorrow's confirmed appointments; build the
#       reminder text; send it through the SMS gateway | Schedule, Appointment, SmsGateway
#
# 3.3 Question: Which class checks that a dentist is not booked twice at the same time? Which
#     class calculates the 50 000 sum fee? Defend both answers with "who has the data".
#     Answer: Double booking is checked by Schedule, because it has all appointments of the
#     dentist with their start times and durations. One Appointment knows only its own time,
#     and Dentist knows the working hours but not the appointments. Schedule asks every
#     Appointment overlaps(new_one), because the overlap uses the start and the duration, and
#     this is the data of Appointment.
#     The 50 000 sum fee is calculated by Appointment.move_fee(now): the 24-hour rule uses the
#     start time, and the start time is the data of Appointment. now comes as a parameter.
#
# 3.4 Question: A new requirement from the clinic's auditor: "We must see who confirmed every
#     appointment." Does this change your decision about the receptionist? What changes on your
#     cards?
#     Answer: Yes. Before, the receptionist was only an actor (a person who clicks "confirm")
#     and we did not keep any data about them. Now we must remember who confirmed and when, so
#     Receptionist (a staff user with an id and a name) becomes a class. Changes on the cards:
#     - Appointment: "confirm" becomes confirm(receptionist, at), it keeps confirmed_by and
#       confirmed_at, and Receptionist is a new collaborator.
#     - New small card Receptionist: know the staff id and the name.
#
# 3.5 Question: Is sending the SMS a responsibility of Appointment? Which class sends it, and
#     what is the relationship between the two classes?
#     Answer: No. Appointment only gives the data (patient, phone, time). Sending an SMS talks
#     to an outside system and it is not a rule of the appointment. If Appointment did it, every
#     Appointment would depend on the SMS provider and could not be tested without real SMS
#     (like in Task 10). ReminderService sends it through SmsGateway.
#     ReminderService -> Appointment is a dependency: it gets the appointments inside one method
#     and does not keep them. ReminderService -> SmsGateway is an association: the gateway is
#     given from outside and kept in a field.
