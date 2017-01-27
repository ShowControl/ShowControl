class MyCode:
    def mycode(self):
        print('test text')
    def othercode(self,aval):
        print('other {}'.format(aval))

x = MyCode()
x.mycode()
eval('x.{}'.format('mycode()'))
eval('x.{}'.format('othercode()'))
