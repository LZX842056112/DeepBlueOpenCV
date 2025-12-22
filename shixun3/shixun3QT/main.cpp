#include "iostream"
#include "Widget.h"
#include <QApplication> //Qt应用程序头文件


int main(int argc, char *argv[])
{
    std::cout << "hello world"<< std::endl;
    // return 0;
    // while(true){} //在Qt程序中，千万不要在主线程写死循环

    QApplication a(argc, argv); //定义应用程序对象,必须传递命令函数参数个数和列表
    Widget w; //定义窗口对象
    w.show(); //显示窗口对象

    return a.exec(); //应用程序事件循坏(死循坏,处理事件，键盘、鼠标、定时器)
}
