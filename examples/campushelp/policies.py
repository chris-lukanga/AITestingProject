"""Source of truth for the fictional Northbridge campus handbook, retrieval and tests."""
POLICIES = [
    {'id': 'registration', 'title': 'Registration and late enrolment',
     'keywords': ['registration', 'register', 'enrol', 'enrollment', 'enrolment'],
     'facts': [
         ('When is the registration deadline?', 'Registration closes on 30 September for the demo academic cycle.'),
         ('How do I register for classes?', 'Register through the student portal: choose modules, check prerequisites, then submit your selection.'),
         ('What documents do I need for registration?', 'Upload your identity document and admission letter before submitting registration.'),
         ('Can I register late?', 'Late registration requires faculty approval; submit a request within 5 working days after the deadline.'),
         ('How do I know my registration is complete?', 'Your registration is complete when the portal shows Registered and provides a confirmation letter.'),
         ('Can I register with an account hold?', 'An account hold must be cleared with Student Accounts before registration can be finalised.'),
         ('Who helps with registration problems?', 'Contact the Registrar through a student support ticket for registration problems.')]},
    {'id': 'fees', 'title': 'Fees and payment arrangements',
     'keywords': ['fees', 'fee', 'payment', 'tuition', 'instalment', 'account balance'],
     'facts': [
         ('When are tuition fees due?', 'Tuition fees are due within 14 calendar days of registration.'),
         ('Can I pay fees in instalments?', 'A payment plan allows 3 monthly instalments after Student Accounts approves your application.'),
         ('How do I apply for a payment plan?', 'Apply for a payment plan in the student portal under Finance and attach proof of income.'),
         ('Where can I see my fee balance?', 'View your current fee balance in the student portal under Finance; this assistant cannot access bank accounts.'),
         ('What payment reference should I use?', 'Use your student number as the payment reference and keep the receipt.'),
         ('How long do fee payments take to appear?', 'Allow 3 working days for a payment to appear on your student account.'),
         ('Who can fix an incorrect fee charge?', 'Open a Student Accounts support ticket with the disputed charge and your receipt; do not include card details.')]},
    {'id': 'financial-aid', 'title': 'Scholarships and financial aid',
     'keywords': ['scholarship', 'bursary', 'financial aid', 'funding'],
     'facts': [
         ('When do scholarship applications close?', 'Scholarship applications close on 15 August in the demo academic cycle.'),
         ('What documents does financial aid need?', 'Financial aid applications require proof of household income, an academic transcript and an identity document.'),
         ('How do I apply for a bursary?', 'Apply in the student portal under Financial Aid and upload the required documents.'),
         ('Is scholarship approval guaranteed?', 'We cannot guarantee scholarship approval; eligibility and available funding determine the decision.'),
         ('How do I check my funding status?', 'Check your funding status in the Financial Aid portal; only the financial aid office can confirm an award.'),
         ('Can I appeal a financial aid decision?', 'Submit a financial aid appeal within 10 working days of the decision with supporting evidence.'),
         ('When do scholarship decisions arrive?', 'Scholarship decisions are normally issued within 20 working days after applications close.')]},
    {'id': 'exams', 'title': 'Examinations and deferred assessments',
     'keywords': ['exam', 'exams', 'examination', 'assessment', 'deferred'],
     'facts': [
         ('How early should I arrive for an exam?', 'Arrive at the exam venue at least 30 minutes before the scheduled start.'),
         ('What must I bring to an exam?', 'Bring your student card and permitted stationery to the exam.'),
         ('What if I am ill on exam day?', 'Apply for a deferred exam within 3 working days of the missed assessment and attach a medical certificate.'),
         ('Where is my exam timetable?', 'Your personal exam timetable is available in the student portal under Assessments.'),
         ('Can I bring my phone into an exam?', 'Phones must be switched off and stored away during an exam; they may not be kept on your desk.'),
         ('Can I arrive late for an exam?', 'Entry is not permitted more than 30 minutes after an exam starts.'),
         ('Who approves a deferred exam?', 'The faculty assessment office reviews deferred exam requests; submission does not guarantee approval.')]},
    {'id': 'appeals', 'title': 'Academic appeals and remarking',
     'keywords': ['appeal', 'appeals', 'remark', 'remarking', 'grade review'],
     'facts': [
         ('When must I request a remark?', 'Submit a remark request within 10 working days of publication of the result.'),
         ('How do I appeal an academic result?', 'Use the Academic Appeals form in the student portal and explain the grounds for review.'),
         ('What evidence should accompany an appeal?', 'Attach the assessment feedback and relevant supporting evidence to an academic appeal.'),
         ('Will a remark always increase my grade?', 'A remark may increase, decrease or leave your grade unchanged.'),
         ('Who decides an academic appeal?', 'An independent faculty panel reviews an academic appeal.'),
         ('How long does an academic appeal take?', 'The faculty aims to respond to an academic appeal within 15 working days.'),
         ('Should I attend classes during an appeal?', 'Continue attending scheduled classes while your academic appeal is being considered.')]},
    {'id': 'accommodation', 'title': 'Residence and accommodation',
     'keywords': ['accommodation', 'residence', 'housing', 'room', 'dorm'],
     'facts': [
         ('When do residence applications close?', 'Residence applications close on 31 August for the demo academic cycle.'),
         ('How do I apply for campus housing?', 'Apply for campus housing through the Residence portal with your admission reference.'),
         ('Is a residence room guaranteed?', 'A residence application does not guarantee a room; offers depend on availability.'),
         ('How do I report a broken fixture in my room?', 'Submit a residence maintenance ticket with the building, room number and fault description.'),
         ('When are residence quiet hours?', 'Residence quiet hours run from 22:00 to 07:00.'),
         ('Can I change my residence room?', 'Request a room transfer from the residence office; written approval is required before moving.'),
         ('How quickly must I accept a residence offer?', 'Accept a residence offer within 7 calendar days or the room may be offered to another applicant.')]},
    {'id': 'library', 'title': 'Library borrowing and study spaces',
     'keywords': ['library', 'book', 'books', 'borrow', 'borrowing'],
     'facts': [
         ('When is the library open?', 'The library is open 08:00 to 20:00 on weekdays and 09:00 to 13:00 on Saturdays; it is closed on Sundays.'),
         ('How many library books can I borrow?', 'Students may borrow up to 6 library books at a time.'),
         ('How long can I keep a library book?', 'The standard library loan period is 14 calendar days.'),
         ('Can I renew a library book?', 'Renew a library book once through the library portal unless another reader has reserved it.'),
         ('How do I book a library study room?', 'Book a library study room through the library portal for up to 2 hours per day.'),
         ('What happens if I lose a library book?', 'Report a lost library book to the library desk; replacement costs are assessed by library staff.'),
         ('Can I use library journals from home?', 'Sign in with your student account to access library journals remotely.')]},
    {'id': 'accessibility', 'title': 'Disability and learning accommodations',
     'keywords': ['accessibility', 'disability', 'accommodations', 'extra time', 'accessible'],
     'facts': [
         ('How do I request disability accommodations?', 'Register with Accessibility Services and submit supporting documentation through their private portal.'),
         ('When should I request extra time for exams?', 'Request exam accommodations at least 20 working days before the first exam.'),
         ('Who approves extra time?', 'Accessibility Services assesses extra time requests and issues an accommodation letter.'),
         ('Should I share my diagnosis with a lecturer?', 'You may share the accommodation letter with a lecturer; you do not need to share your diagnosis.'),
         ('What if I develop a temporary disability?', 'Contact Accessibility Services for temporary adjustments following an injury or short-term impairment.'),
         ('Can I request accessible course materials?', 'Request accessible course materials from Accessibility Services as early as possible.'),
         ('Where are disability documents stored?', 'Disability documents are held privately by Accessibility Services and are not part of the public handbook.')]},
    {'id': 'wellbeing', 'title': 'Student wellbeing and counselling',
     'keywords': ['wellbeing', 'counselling', 'counseling', 'mental health', 'stress', 'anxious'],
     'facts': [
         ('How do I book counselling?', 'Book a counselling appointment through the Student Wellbeing portal.'),
         ('Does student counselling cost anything?', 'Enrolled students can access up to 6 counselling sessions per academic year at no charge.'),
         ('Is student counselling confidential?', 'Counselling is confidential, subject to safeguarding and legal obligations explained by the counsellor.'),
         ('What are the wellbeing office hours?', 'The Student Wellbeing office is open 09:00 to 16:00 on weekdays.'),
         ('What can I do about study stress?', 'For study stress, contact Student Wellbeing and ask your academic adviser about workload support.'),
         ('Can the wellbeing assistant diagnose me?', 'This assistant cannot diagnose conditions; a qualified health professional can assess your needs.'),
         ('What should I do in an immediate emergency?', 'If you are in immediate danger, contact local emergency services or campus security and seek nearby help.')]},
    {'id': 'it-support', 'title': 'Campus accounts and IT support',
     'keywords': ['password', 'wifi', 'wi-fi', 'login', 'log in', 'it support', 'account locked', 'mfa'],
     'facts': [
         ('How do I reset my password?', 'Reset your password using the Forgot password link on the student portal.'),
         ('What if my campus account is locked?', 'After 5 failed sign-in attempts your account is locked for 15 minutes; use password reset or contact IT Support.'),
         ('How do I connect to campus wifi?', 'Connect to CampusStudent Wi-Fi and sign in with your student email and password.'),
         ('Should I send IT support my password?', 'Never share your password or one-time code in chat or a support ticket.'),
         ('What if I lose my MFA device?', 'Contact IT Support for identity verification and MFA recovery.'),
         ('How do I report a suspicious email?', 'Report a suspicious email through the IT Support portal without opening its attachments.'),
         ('When is IT support available?', 'IT Support is available 08:00 to 17:00 on weekdays.')]},
    {'id': 'withdrawal', 'title': 'Module changes and withdrawal',
     'keywords': ['withdraw', 'withdrawal', 'drop', 'module change', 'refund'],
     'facts': [
         ('When can I change my modules?', 'Module changes are permitted during the first 10 working days of teaching, subject to prerequisites and capacity.'),
         ('How do I withdraw from a module?', 'Submit a module withdrawal request in the student portal and discuss the academic impact with your adviser.'),
         ('Do I get a refund if I withdraw?', 'Refund eligibility depends on the withdrawal date; Student Accounts must confirm the amount.'),
         ('Can I just stop attending a module?', 'Stopping attendance does not withdraw you from a module; submit the formal withdrawal request.'),
         ('Can withdrawal affect my funding?', 'Module withdrawal may affect funding and progression; consult Financial Aid and your academic adviser first.'),
         ('Can I reverse a module withdrawal?', 'Contact the Registrar to request reversal of a module withdrawal; reinstatement is not guaranteed.'),
         ('Who can explain module prerequisites?', 'Your faculty academic adviser can explain module prerequisites before you change your selection.')]},
    {'id': 'support', 'title': 'Student support tickets and privacy',
     'keywords': ['support ticket', 'support tickets', 'student services', 'ticket', 'tickets'],
     'facts': [
         ('How do support tickets work?', 'Support tickets route questions to the student services team; asking for information does not create a ticket.'),
         ('How do I create a support ticket?', 'Describe the issue, ask to create a support ticket, then confirm the draft before it is submitted.'),
         ('How long does student support take to respond?', 'Student Services aims to respond within 2 working days.'),
         ('Can I see another student support ticket?', 'You may view only your own support tickets.'),
         ('What information should I put in a support ticket?', 'Include the issue and relevant dates in a support ticket; omit passwords, banking details and medical records.'),
         ('Can I close my support ticket?', 'You can close your own support ticket once the issue is resolved.'),
         ('Are student support tickets public?', 'Student support tickets are private and access is restricted to the owner and authorised support staff.')]},
]

for policy in POLICIES:
    policy.update(owner='public', version='Demo handbook v1')
    policy['text'] = '\n'.join(answer for _, answer in policy['facts'])


def retrieve(message, previous_ids=()):
    """Rank public policies using phrase and token overlap, with follow-up context."""
    import re
    exact = [p for p in POLICIES if any(message.strip().lower() == q.lower() for q, _ in p['facts'])]
    if exact:
        return exact
    tokens = set(re.findall(r'[a-z]+', message.lower()))
    stop = {'what', 'when', 'where', 'how', 'can', 'do', 'i', 'a', 'the', 'is', 'my', 'to', 'for', 'in', 'of', 'and', 'it', 'are', 'with', 'should'}
    query = tokens - stop
    followup = bool(re.search(r'\b(what about|and (what|how|when)|that|this|it|those|more|documents|deadline)\b', message.lower()))
    ranked = []
    for policy in POLICIES:
        keyword_score = sum(4 for word in policy['keywords'] if re.search(r'\b' + re.escape(word) + r'\b', message.lower()))
        overlap = max(len(query & (set(re.findall(r'[a-z]+', q.lower())) - stop)) for q, _ in policy['facts'])
        score = keyword_score + overlap
        if followup and policy['id'] in previous_ids:
            score += 5
        if keyword_score or overlap >= 2 or (followup and policy['id'] in previous_ids):
            ranked.append((score, policy))
    ranked.sort(key=lambda pair: pair[0], reverse=True)
    return [p for score, p in ranked[:2] if score >= ranked[0][0] - 2]
