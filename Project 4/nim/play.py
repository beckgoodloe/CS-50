from nim import train, play

ai = train(10000)
while(True):
    print("NEW GAME!!!")
    play(ai)
