class testClass():
    def __init__(self):
        self.value = 0

    def changeValue(self):
        self.value = self.value +1
        print(self.value)
    def printer(self):
        printTest()

def printTest():
    print("test")

if __name__ == "__main__":
    newTestClass = testClass()
    newTestClass.changeValue()
    newTestClass.printer()

