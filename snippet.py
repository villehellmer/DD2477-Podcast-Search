import json
import numpy as np

with open('test.json', 'r') as f:
    data = json.load(f)

transcripts = [d['transcript'] for d in data]
all_words = [[w['word'] for w in d['words']] for d in data]
all_start = [np.array([s['startTime'][:-1] for s in d['words']]).astype(float) for d in data]
all_end = [np.array([e['endTime'][:-1] for e in d['words']]).astype(float) for d in data]

def get_snippet_part(transcript, words, start, end, word_index, pre=60, post=60):

    if word_index == -1:
        word_index = len(words) - 1

    dur = np.subtract(end, start)
    w_dur = dur[word_index]
    pre -= w_dur/2
    post -= w_dur/2

    snippet = []

    i = word_index
    window = 0
    for i in range(word_index-1, -1, -1):
        snippet.append(words[i])
        window += dur[i]
        if window >= pre:
            break

    start_index = i

    snippet.reverse()
    snippet.append(words[word_index])

    i = word_index
    window = 0
    for i in range(word_index+1, len(words)):
        snippet.append(words[i])
        window += dur[i]
        if window >= post:
            break

    end_index = i

    start_time = start[start_index]
    end_time = end[end_index]
    is_complete = end_time - start_time >= pre + post

    return (snippet, start_time, end_time, is_complete)

def get_snippet(transcripts, all_words, all_start, all_end, tr_index, w_index, pre=60, post=60):

    # get the snippet in the current transcript
    snippet, start_time, end_time, complete = get_snippet_part(
        transcripts[tr_index], all_words[tr_index],
        all_start[tr_index], all_end[tr_index],
        w_index, pre=pre, post=post
    )

    # we're done, everything was in one
    if complete:
        return snippet, start_time, end_time
    # check previous and successive transcripts
    else:
        # time we need to fill
        remaining_time = (pre + post) - (end_time - start_time)
        pre_rem_time = min(pre, remaining_time/2)
        post_rem_time = min(post, remaining_time - pre_rem_time)

        # check indexes
        can_backwards = tr_index-1 >= 0
        can_forward = tr_index+1 < len(transcripts)
        all_snippet = []

        if can_backwards:
            # previous part, start from last word
            # of previous transcript and go backward
            pre_snippet, pre_start_time, pre_end_time = get_snippet(
                transcripts, all_words,
                all_start, all_end,
                tr_index-1, -1, pre=pre_rem_time, post=0
            )
            # update values
            all_snippet.extend(pre_snippet)
            start_time = pre_start_time

        all_snippet.extend(snippet)

        if can_forward:
            # successive part, start from first word
            # of next transcript and go forward
            post_snippet, post_start_time, post_end_time = get_snippet(
                transcripts, all_words,
                all_start, all_end,
                tr_index+1, 0, pre=0, post=post_rem_time
            )
            # update values
            all_snippet.extend(post_snippet)
            end_time = post_end_time


        return all_snippet, start_time, end_time


print(get_snippet(transcripts,
            all_words,
            all_start,
            all_end,
            0, 16, pre=5, post=100))

