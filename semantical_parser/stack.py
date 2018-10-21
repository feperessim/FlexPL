class Stack:
    def __init__(self):
        self.items = []
        
    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items) -1]

    def size(self):
        return len(self.items)
    
    def printStack(self):
        n = 0
        for scope in self.items:
            print("Scope n: " + str(n))
            n+=1
            for varList in scope.items:
                print("Token: " + varList.token)
                print("id: " + str(varList.id))
                print("Var Name: " +varList.varName)
                print("Data Type: " + varList.dataType.dtype)
                print("\n")
