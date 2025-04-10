import random
class card:

    def makeAtr():
        cardArr = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
        for i in range(len(cardArr)): 
            weights = [0,0,0,0,1,1,1,1,1]
            if i==2:
                for k in range(len(cardArr[0])):
                    count = 0
                    for j in range(0,2):
                        count+= cardArr[j][k]
                    if count ==0:
                        cardArr[2][k] = 1
                        weights.pop()

            random.shuffle(weights)

            for j in range(len(cardArr[i])):
                if cardArr[i][j]== 0:
                    if weights.pop()==1:
                        cardArr[i][j] =1
        
        grid = [[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]] 
        for i in range(0,9):
            dup = []
            j= 0
            while j < 3:
                rand = random.randint(i*10+1,i*10+10)
                if dup.count((rand)) == 0:
                    dup.append((rand))
                    j+=1
            dup.sort()
            for k in range(0,3):
                grid[k][i] = dup[k]
            

        cardStr = ""
        for i in range(0,26):
            cardArr[i%3][i//3] = cardArr[i%3][i//3] * grid[i%3][i//3] 
            cardStr+= (cardArr[i%3][i//3].__str__()+"|")
            
        print(cardStr)
        return cardArr, cardStr

    def checkState(self, cardStr):
        arr =[[],[],[]]
        cardarr = cardStr.split("|")
        for i in range(0,26):
            if cardarr[i]!="0":
                arr[i%3].append(int(cardarr[i]))
        totalCard = [arr[0],arr[1],arr[2]]
        self.condensed = totalCard
        return totalCard


    arr, str = makeAtr()


    
            
            


    
        

    

        




