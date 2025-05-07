system:
# Definition

**Call to Action Quality** evaluates how clear, relevant, and motivating the call to action is in the model’s response, based on a 1–5 scale.

Score 1: There is no call to action, or the one included is confusing, irrelevant, or misleading.
Score 5: The CTA is crystal clear, action-oriented, well-aligned with the content, and highly motivating. It uses strong yet natural language and gives the reader a compelling reason to take action.

The examples below show the Call to Action Quality score with reason for a question and response.

**Example 1**
question: How can I start learning about AI?
response: That’s up to you. Everyone learns differently.
output: {"score": 1, "reason": "The response avoids giving guidance and lacks any clear or motivating call to action."}

**Example 2**
question: How can I improve my resume for tech roles?
response: Try using strong action verbs and highlight measurable impact. You can also book a free resume review session this week to get expert feedback.
output: {"score": 5, "reason": "The CTA is clear, specific, and directly aligned with the user's goal—offering a next step that adds immediate value."}

**Here the actual conversation to be scored:**
question: {{query}}
predicted answer: {{response}}
output: