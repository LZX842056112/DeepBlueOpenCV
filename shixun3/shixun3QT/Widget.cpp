#include "Widget.h"
#include <QApplication>
#include <QDebug>
#include <QMessageBox>

Widget::Widget(QWidget *parent)
    : QWidget(parent)
{
    // 设置窗口可以接收键盘焦点
    setFocusPolicy(Qt::StrongFocus);

    // 设置窗口标题，以便识别
    setWindowTitle("按任意键结束程序");

    // 设置窗口大小
    resize(400, 300);
}

Widget::~Widget()
{
}

// 2.2.1、在VS中建立一个Console工程
void Widget::keyPressEvent(QKeyEvent *event)
{
    // 退出应用程序
    QApplication::quit();
}
