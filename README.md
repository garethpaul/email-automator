*Retrieving Email*
1. Google Mail APIs scan my inbox every 3 minutes.
2. New emails are sent to a task queue for processing.
3. Task queues get flushed every 5 minutes.

*Processing Email*
1. Once an email is sent it is stripped (typically emails are sent with HTML) so we strip the email to plain txt.
2. In plain text format the emails are then removed of their common words (ands, ifs, thens).
3. A somewhat cohesive list of words is set and then they are sent to a hash map (think a much smaller version of Google Search).
4. The list of words is compared to the hashmap with email responses.

*Replying Email*
1. The output of processing is a plain text email.
2. We then push the output from processing back into the Google Mail APIs
3. The sender receives a unique and debatable humorous  reply
