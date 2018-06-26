import PollableQueue.PollableQueue as PollableQueue
import select
import threading
import time


def writeThread(pollqueues, fin):
    flag = True

    while flag:
        try:
            """
            You can use select.select(pollqueue, [], [], 0) for never block,
            note due to C level implementation, can't use timeout=0
            But that's not pollablequeue designed for
            
            So you should use select.select(pollqueue, [], []) for always block,
            and send your customized signal to break from block
            """
            can_read, _, _ = select.select(pollqueues, [], [])
            for r in can_read:
                item = r.get()
                if item == fin:
                    print("Received fin")
                    break
                else:
                    print(item)
            """
            Check continue flag here. Because pollqueues is a list, if you only
            pass 1 pollqueue, then you can just check pollqueues[0].continuum().
            If you pass multiple pollqueues, you can iterate through pollqueues
            and check if any of them call end()
            """
            for pollqueue in pollqueues:
                flag = flag and pollqueue.continuum()
        except Exception as e:
            print(e)
            pass


if __name__ == "__main__":
    #customized signal to break from block
    fin = 'Fin'

    pollqueue1 = PollableQueue.PollableQueue()
    pollqueue2 = PollableQueue.PollableQueue()

    try:
        #start write thread first
        t = threading.Thread(name='write thread', target=writeThread, args=([pollqueue1,pollqueue2],fin,))
        t.start()

        """
        now feed data to pollqueue, you can use thread to produce your data
        """
        pollqueue1.put('poll1+1')
        pollqueue2.put('poll2+2')
        pollqueue1.put('poll1+3')

        # wait for result queue empty
        empty = False
        while not empty:
            time.sleep(1)
            for pollqueue in [pollqueue1, pollqueue2]:
                empty = empty or pollqueue.empty()

        print("No more need to write, terminating write thread")
        # after result queue empty, set write flag false
        pollqueue1.end(fin)

        # wait for write thread join
        print("Waiting for write thread join")
        t.join()
        pollqueue1.close()
    except Exception as e:
        print(e)
        pass