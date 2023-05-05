import json
import numpy as np

def get_elems(data):
    data = data['sequences']
    transcripts = [d['transcript'] for d in data]
    all_words = [[w['word'] for w in d['words']] for d in data]
    all_start = [np.array([s['startTime'][:-1] for s in d['words']]).astype(float) for d in data]
    all_end = [np.array([e['endTime'][:-1] for e in d['words']]).astype(float) for d in data]

    return transcripts, all_words, all_start, all_end

def get_snippet_part(transcript, words, start, end, word_index, pre=60, post=60):

    if word_index == -1:
        word_index = len(words) - 1

    snippet = []
    w_start = start[word_index]
    w_end = end[word_index]
    w_dur = (w_end - w_start)

    i = word_index
    if pre != 0:
        pre -= w_dur/2
        for i in range(word_index-1, -1, -1):
            snippet.append(words[i])
            if w_start - start[i] >= pre:
                break

    start_index = i

    snippet.reverse()
    snippet.append(words[word_index])

    i = word_index
    if post != 0:
        post -= w_dur/2
        for i in range(word_index+1, len(words)):
            snippet.append(words[i])
            if end[i] - w_end >= post:
                break

    end_index = i

    start_time = start[start_index]
    end_time = end[end_index]
    is_complete = end_time - start_time >= pre + post

    return (snippet, start_time, end_time, is_complete)

# episode is the json object as returned by elastic (cfr test.json)
# tr_index is the index of the transcript where the word is in episode['sequences']
# w_index is the index of the word in the transcript "episode['sequences'][tr_index]", defaults to len(transcript)/2
def get_snippet(episode, tr_index, w_index=None, pre=60, post=60):

    transcripts, all_words, all_start, all_end = get_elems(episode)

    if w_index = None:
        w_index = len(transcripts[tr_index])//2

    # get the snippet in the current transcript
    snippet, start_time, end_time, complete = get_snippet_part(
        transcripts[tr_index], all_words[tr_index],
        all_start[tr_index], all_end[tr_index],
        w_index, pre=pre, post=post
    )

    # we're done, everything was in one
    if complete:
        return [' '.join(snippet)], start_time, end_time
    # check previous and successive transcripts
    else:
        # time we need to fill
        remaining_time = (pre + post) - abs(end_time - start_time)

        if pre == 0:
            post_rem_time = remaining_time
            pre_rem_time = 0
        elif post == 0:
            pre_rem_time = remaining_time
            post_rem_time = 0
        else:
            pre_rem_time = min(pre, remaining_time/2)
            post_rem_time = min(post, remaining_time - pre_rem_time)


        # check indexes
        can_backwards = pre_rem_time != 0 and tr_index-1 >= 0
        can_forward = post_rem_time != 0 and tr_index+1 < len(transcripts)
        all_snippet = []

        if can_backwards:
            # previous part, start from last word
            # of previous transcript and go backward
            pre_snippet, pre_start_time, pre_end_time = get_snippet(
                episode, tr_index-1, -1, pre=pre_rem_time, post=0
            )
            # update values
            all_snippet.append(' '.join(pre_snippet))
            start_time = pre_start_time

        all_snippet.append(' '.join(snippet))

        if can_forward:
            # successive part, start from first word
            # of next transcript and go forward
            post_snippet, post_start_time, post_end_time = get_snippet(
                episode, tr_index+1, 0, pre=0, post=post_rem_time
            )
            # update values
            all_snippet.append(' '.join(post_snippet))
            end_time = post_end_time


        return all_snippet, start_time, end_time
