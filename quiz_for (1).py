print("WELCOME TO AMSS'S GAME , YOU'RE IN FOR A RIDE ")

play=input("Are You Ready to Give Your Best Shot At This?(yes/no) ")
if play.lower()=="yes":
    print("let's get started!".upper())
else:
    print("you coward!".upper())

score=0

answer=input("what would you give amss if she were mad? ")
if answer.lower() != "food":
    print("She's gonna be dissapointed in you , However , its FOOD")
else:
    print("OOF , MAKING HER PROUD AND ALL , NOICE!")
    score+=1

answer=input("What is her favourite color? ")
if answer.lower() != "yellow":
    print("How are you even- , anyway , its yellow yellow , you dirty fellow!")
else:
    print("She definitely did'nt see that one one coming")
    score+=1

answer=input("What is her favourite food to eat?(Rice item) ")
if answer.lower() != "biryani":
    print("Didn't get it right? It's Biryani , Now go order her some!")
else:
    print("OO NOICE , you just figured out the way to her HEART!")
    score+=1

answer=input("What is her favourite thing to do when she has nothing to do? ")
if answer.lower() != "eat":
    print("Time to quit coding and do a PhD on her!")
else:
    print("cool cool cool cool cool".upper())
    score+=1

answer=input("who is the most funniest/beautiful and your favourite person in the whole wide world? ")
if answer.lower() != "amrutha":
    print("OK NOW , SHE SAYS BYE")
else:
    print("OOF , YOU GON GET LUCKY MATE!")
    score+=1

print("you scored "+str(score) + "out of five")
print("Thats "+str((score/5)*100)+"%")