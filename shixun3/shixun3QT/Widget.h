#ifndef WIDGET_H
#define WIDGET_H

#include <QWidget> //Qt窗口基类头文件
#include <QKeyEvent>

class Widget : public QWidget //自定义窗口类，继承自Qwidget
{
    Q_OBJECT //使用Qt信号和槽机制必须包含此宏

public:
    Widget(QWidget *parent = nullptr);
    ~Widget();

protected:
    // 2.2.1、在VS中建立一个Console工程
    void keyPressEvent(QKeyEvent* event) override;  // 重写键盘按下事件

};
#endif // WIDGET_H
