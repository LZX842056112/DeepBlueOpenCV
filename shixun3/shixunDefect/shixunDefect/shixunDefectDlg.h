
// shixunDefectDlg.h: 头文件
//

#pragma once
#include <atlimage.h>  // 添加CImage头文件


// CshixunDefectDlg 对话框
class CshixunDefectDlg : public CDialogEx
{
// 构造
public:
	CshixunDefectDlg(CWnd* pParent = nullptr);	// 标准构造函数

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_SHIXUNDEFECT_DIALOG };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV 支持


// 实现
protected:
	HICON m_hIcon;
	CImage m_image;  // 当前显示的图片
	// Picture Control控件
	CStatic m_picture; // Picture Control控件
	CFont m_fontBig;

	// 生成的消息映射函数
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnBnClickedButton1();
};
