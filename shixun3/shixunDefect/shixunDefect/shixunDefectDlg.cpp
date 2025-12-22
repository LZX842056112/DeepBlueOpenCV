
// shixunDefectDlg.cpp: 实现文件
//

#include "pch.h"
#include "framework.h"
#include "shixunDefect.h"
#include "shixunDefectDlg.h"
#include "afxdialogex.h"
#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <filesystem>
#include <chrono>
#include <algorithm>
#include <optional>
#include <atlimage.h>  // 添加CImage头文件

namespace fs = std::filesystem;
using namespace cv;


#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// 用于应用程序“关于”菜单项的 CAboutDlg 对话框

class CAboutDlg : public CDialogEx
{
public:
	CAboutDlg();

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_ABOUTBOX };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

// 实现
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(IDD_ABOUTBOX)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()


// CshixunDefectDlg 对话框



CshixunDefectDlg::CshixunDefectDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_SHIXUNDEFECT_DIALOG, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CshixunDefectDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
    // 绑定
    DDX_Control(pDX, IDCANCEL, m_picture);
}

BEGIN_MESSAGE_MAP(CshixunDefectDlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_BUTTON1, &CshixunDefectDlg::OnBnClickedButton1)
END_MESSAGE_MAP()


// CshixunDefectDlg 消息处理程序

BOOL CshixunDefectDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// 将“关于...”菜单项添加到系统菜单中。

	// IDM_ABOUTBOX 必须在系统命令范围内。
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != nullptr)
	{
		BOOL bNameValid;
		CString strAboutMenu;
		bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
		ASSERT(bNameValid);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// 设置此对话框的图标。  当应用程序主窗口不是对话框时，框架将自动
	//  执行此操作
	SetIcon(m_hIcon, TRUE);			// 设置大图标
	SetIcon(m_hIcon, FALSE);		// 设置小图标

	// TODO: 在此添加额外的初始化代码
    // 设置Picture Control的背景色为白色
    m_picture.ModifyStyle(0, SS_NOTIFY);
    m_picture.ModifyStyle(0, SS_SUNKEN);
    m_fontBig.CreatePointFont(
        300,            // 字号 × 10 → 20号字
        TEXT("微软雅黑") // 支持中文
    );

    GetDlgItem(IDC_STATIC)->SetFont(&m_fontBig);

	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
}

void CshixunDefectDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialogEx::OnSysCommand(nID, lParam);
	}
}

// 如果向对话框添加最小化按钮，则需要下面的代码
//  来绘制该图标。  对于使用文档/视图模型的 MFC 应用程序，
//  这将由框架自动完成。

void CshixunDefectDlg::OnPaint()
{
    // 处理最小化状态绘制
	if (IsIconic())
	{
		CPaintDC dc(this); // 用于绘制的设备上下文

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 使图标在工作区矩形中居中
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 绘制图标
		dc.DrawIcon(x, y, m_hIcon);
	}
	// 正常状态下的绘制
	else
	{
		CDialogEx::OnPaint();
        if (!m_image.IsNull())
        {
            // 获取绘制区域
            CRect rect;
            m_picture.GetClientRect(&rect);
            //获取设备上下文
            CDC* pDC = m_picture.GetDC();
            if (!pDC)
                return;

            // 清除背景
            CBrush whiteBrush(RGB(255, 255, 255));
            pDC->FillRect(&rect, &whiteBrush);

            // 获取图片原始尺寸
            int imageWidth = m_image.GetWidth();
            int imageHeight = m_image.GetHeight();

            // 计算缩放比例（保持宽高比）
            double widthRatio = (double)rect.Width() / imageWidth;
            double heightRatio = (double)rect.Height() / imageHeight;
            double scaleRatio = std::min(widthRatio, heightRatio);  // 使用较小的比例，确保图片完全显示

            // 计算缩放后的尺寸
            int scaledWidth = (int)(imageWidth * scaleRatio);
            int scaledHeight = (int)(imageHeight * scaleRatio);

            // 计算居中位置
            int x = (rect.Width() - scaledWidth) / 2;
            int y = (rect.Height() - scaledHeight) / 2;

            // 设置缩放模式为HALFTONE，使缩放效果更好
            SetStretchBltMode(pDC->GetSafeHdc(), HALFTONE);

            // 缩放并绘制图片
            m_image.StretchBlt(pDC->GetSafeHdc(),
                x, y, scaledWidth, scaledHeight,
                0, 0, imageWidth, imageHeight, SRCCOPY);
            // 释放之前获取的设备上下文，避免资源泄漏
            m_picture.ReleaseDC(pDC);
        }
	}
}

//当用户拖动最小化窗口时系统调用此函数取得光标
//显示。
HCURSOR CshixunDefectDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}


// 预定义常用结构元素
cv::Mat KERNEL_7 = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(7, 7));
cv::Mat KERNEL_3 = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
cv::Mat KERNEL_25_ELLIPSE = cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(25, 25));

// 缺陷类型枚举
enum class DefectType {
	INDENTATION,
	SPOT,
	DEBRIS,
	DARK,
	CLEAN
};

// 缺陷信息结构体
struct DefectInfo {
	DefectType type;
	cv::Rect rect;  // 外接矩形
	cv::Rect defect_rect;  // 凹痕专用
	cv::Point p_left;  // 凹痕专用
	cv::Point p_right;  // 凹痕专用
	std::vector<cv::Point> contour;  // 凹痕专用
	cv::Scalar color;  // 绘制颜色
};

// 使用GrabCut算法获取前景掩码
std::pair<cv::Mat, bool> get_foreground_mask(const cv::Mat& img, double scale_factor = 0.06, int iter_count = 2) {
    if (img.empty()) {
        return { cv::Mat(), false };
    }

    int h = img.rows;
    int w = img.cols;

    // 计算缩小后的尺寸
    int sw = static_cast<int>(w * scale_factor);
    int sh = static_cast<int>(h * scale_factor);

    // 缩小图像
    cv::Mat small_img;
    cv::resize(img, small_img, cv::Size(sw, sh), 0, 0, cv::INTER_AREA);

    // 定义前景矩形区域
    cv::Rect rect(
        static_cast<int>(sw * 0.2),
        static_cast<int>(sh * 0.05),
        static_cast<int>(sw * 0.6),
        static_cast<int>(sh * 0.9)
    );

    // 创建掩码
    cv::Mat mask(sh, sw, CV_8UC1, cv::Scalar(0));
    cv::Mat bgdModel, fgdModel;

    try {
        cv::grabCut(small_img, mask, rect, bgdModel, fgdModel, iter_count, cv::GC_INIT_WITH_RECT);
    }
    catch (const cv::Exception& e) {
        std::cerr << "GrabCut error: " << e.what() << std::endl;
        return { cv::Mat(), false };
    }

    // 处理掩码：将确定前景(1)和可能前景(3)设为1，其他设为0
    cv::Mat mask_bin = cv::Mat::zeros(mask.size(), CV_8UC1);
    mask_bin.setTo(255, mask == 1);  // 确定前景
    mask_bin.setTo(255, mask == 3);  // 可能前景

    // 恢复到原始尺寸
    cv::Mat result_mask;
    cv::resize(mask_bin, result_mask, cv::Size(w, h), 0, 0, cv::INTER_NEAREST);

    return { result_mask, true };
}

// 检测凹痕
std::optional<DefectInfo> find_indentation_defect(const cv::Mat& img, const cv::Mat& hsv, const cv::Mat& mask) {
    // 定义蓝色的HSV范围
    cv::Mat blue;
    cv::inRange(hsv, cv::Scalar(40, 170, 40), cv::Scalar(130, 255, 255), blue);

    // 只在前景区域内检测蓝色
    cv::bitwise_and(blue, mask, blue);

    // 形态学操作
    cv::morphologyEx(blue, blue, cv::MORPH_CLOSE, KERNEL_7);
    cv::morphologyEx(blue, blue, cv::MORPH_OPEN, KERNEL_7);

    // 寻找轮廓
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(blue, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    if (contours.empty()) {
        return std::nullopt;
    }

    // 找到最大的蓝色区域
    auto max_contour = std::max_element(contours.begin(), contours.end(),
        [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
            return cv::contourArea(a) < cv::contourArea(b);
        });

    cv::Rect blue_rect = cv::boundingRect(*max_contour);

    // 宽度过滤
    if (blue_rect.width < 450) {
        return std::nullopt;
    }

    // 转换为点集
    std::vector<cv::Point> pts;
    for (const auto& pt : *max_contour) {
        pts.push_back(pt);
    }

    // 定义感兴趣区域的上限
    double y_limit = blue_rect.y + blue_rect.height * 0.05;

    // 筛选顶部点
    std::vector<cv::Point> top_pts;
    for (const auto& pt : pts) {
        if (pt.y < y_limit) {
            top_pts.push_back(pt);
        }
    }

    if (top_pts.empty()) {
        return std::nullopt;
    }

    // 寻找左右角点
    cv::Point p_left = top_pts[0];
    cv::Point p_right = top_pts[0];

    for (const auto& pt : top_pts) {
        // 左角点：x+y最小
        if ((pt.x + pt.y) < (p_left.x + p_left.y)) {
            p_left = pt;
        }

        // 右角点：y - x 最小 (y较小且x较大)
        if ((pt.y - pt.x) < (p_right.y - p_right.x)) {
            p_right = pt;
        }
    }

    if (p_right.x == p_left.x) {
        return std::nullopt;
    }

    // 选取ROI点
    std::vector<cv::Point> roi_pts;
    for (const auto& pt : pts) {
        if (pt.x > p_left.x && pt.x < p_right.x && pt.y < y_limit) {
            roi_pts.push_back(pt);
        }
    }

    if (roi_pts.empty()) {
        return std::nullopt;
    }

    // 计算斜率和检测凹痕
    double slope = static_cast<double>(p_right.y - p_left.y) / (p_right.x - p_left.x);

    int defect_count = 0;
    cv::Rect defect_rect;
    std::vector<cv::Point> defect_pts;

    for (const auto& pt : roi_pts) {
        double y_expected = p_left.y + slope * (pt.x - p_left.x);

        if (pt.y > y_expected) {  // 向下凹陷
            defect_count++;
            defect_pts.push_back(pt);
        }
    }

    double ratio = static_cast<double>(defect_count) / roi_pts.size();

    if (ratio <= 0.5) {
        return std::nullopt;
    }

    // 计算凹痕区域外接矩形
    if (!defect_pts.empty()) {
        defect_rect = cv::boundingRect(defect_pts);
    }

    DefectInfo info;
    info.type = DefectType::INDENTATION;
    info.rect = blue_rect;
    info.defect_rect = defect_rect;
    info.p_left = p_left;
    info.p_right = p_right;
    info.contour = *max_contour;
    info.color = cv::Scalar(0, 0, 255);  // BGR: 红色

    return info;
}

// 褐色斑点检测
std::optional<DefectInfo> find_brown_candidate(const cv::Mat& hsv, const cv::Mat& mask) {
    // 定义褐色的HSV范围
    cv::Mat brown;
    cv::inRange(hsv, cv::Scalar(10, 80, 0), cv::Scalar(30, 255, 200), brown);

    // 只在前景区域内检测褐色
    cv::bitwise_and(brown, mask, brown);

    // 形态学开操作
    cv::morphologyEx(brown, brown, cv::MORPH_OPEN, KERNEL_3);

    // 寻找轮廓
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(brown, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    cv::Rect best_rect;
    double best_area = 0;

    for (const auto& contour : contours) {
        double area = cv::contourArea(contour);
        if (area > best_area) {
            best_rect = cv::boundingRect(contour);
            best_area = area;
        }
    }

    if (best_area > 0) {
        DefectInfo info;
        info.type = DefectType::SPOT;
        info.rect = best_rect;
        info.color = cv::Scalar(0, 165, 255);  // BGR: 橙色
        return info;
    }

    return std::nullopt;
}

// 检测碎片缺陷
std::optional<DefectInfo> find_debris_candidate(const cv::Mat& gray, const cv::Mat& mask, const cv::Size& img_shape) {
    // 创建亮度掩码，排除过亮区域
    cv::Mat bright;
    cv::threshold(gray, bright, 200, 255, cv::THRESH_BINARY_INV);

    // 结合前景掩码和亮度掩码
    cv::Mat valid;
    cv::bitwise_and(mask, bright, valid);

    // Canny边缘检测
    cv::Mat edges;
    cv::Canny(gray, edges, 30, 100);
    cv::bitwise_and(edges, valid, edges);

    // 形态学操作
    cv::dilate(edges, edges, KERNEL_3, cv::Point(-1, -1), 2);
    cv::morphologyEx(edges, edges, cv::MORPH_CLOSE, KERNEL_3);

    // 寻找轮廓
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(edges, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    std::vector<std::vector<cv::Point>> candidates;

    for (const auto& contour : contours) {
        cv::Rect rect = cv::boundingRect(contour);

        // 宽高比过滤
        if (rect.height == 0 || static_cast<float>(rect.width) / rect.height > 5) {
            continue;
        }

        candidates.push_back(contour);
    }

    if (candidates.empty()) {
        return std::nullopt;
    }

    // 选择面积最大的候选轮廓
    auto best_contour = std::max_element(candidates.begin(), candidates.end(),
        [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
            return cv::contourArea(a) < cv::contourArea(b);
        });

    cv::Rect best_rect = cv::boundingRect(*best_contour);

    // 最终尺寸检查
    if (best_rect.width > img_shape.width * 0.5 || best_rect.height > img_shape.height * 0.5) {
        return std::nullopt;
    }

    DefectInfo info;
    info.type = DefectType::DEBRIS;
    info.rect = best_rect;
    info.color = cv::Scalar(0, 0, 255);  // BGR: 红色
    return info;
}

// 暗斑检测
std::optional<DefectInfo> find_dark_spot(const cv::Mat& hsv, const cv::Mat& mask) {
    int h = mask.rows;
    int w = mask.cols;

    // 计算腐蚀核大小
    int k = static_cast<int>(std::min(w, h) * 0.04);
    if (k % 2 == 0) k++;

    // 创建结构元素
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(k, k));

    // 腐蚀掩码
    cv::Mat roi_mask;
    cv::erode(mask, roi_mask, kernel);

    // 定义暗色区域的HSV范围
    cv::Mat color_mask;
    cv::inRange(hsv, cv::Scalar(0, 0, 120), cv::Scalar(180, 255, 150), color_mask);

    // 在腐蚀后的前景区域内检测暗色
    cv::Mat valid_mask;
    cv::bitwise_and(color_mask, roi_mask, valid_mask);

    // 合并相邻的细碎暗点
    cv::Mat merged_mask;
    cv::dilate(valid_mask, merged_mask, KERNEL_25_ELLIPSE, cv::Point(-1, -1), 3);

    // 寻找轮廓
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(merged_mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    cv::Rect best_rect;
    double best_area = 0;

    for (const auto& contour : contours) {
        cv::Rect rect = cv::boundingRect(contour);

        // 提取对应区域
        cv::Mat roi = valid_mask(rect);
        double area = cv::countNonZero(roi);

        // 面积过滤和形状过滤
        if (area > 20 && area < 400) {
            float ratio = static_cast<float>(rect.width) / rect.height;
            if (ratio > 0.5 && ratio < 2.0) {
                if (area > best_area) {
                    best_area = area;
                    best_rect = rect;
                }
            }
        }
    }

    if (best_area > 0) {
        DefectInfo info;
        info.type = DefectType::DARK;
        info.rect = best_rect;
        info.color = cv::Scalar(128, 0, 128);  // BGR: 紫色
        return info;
    }

    return std::nullopt;
}

// 缺陷类型转字符串
std::string defect_type_to_string(DefectType type) {
    switch (type) {
    case DefectType::INDENTATION: return "INDENTATION";
    case DefectType::SPOT: return "SPOT";
    case DefectType::DEBRIS: return "DEBRIS";
    case DefectType::DARK: return "DARK";
    case DefectType::CLEAN: return "CLEAN";
    default: return "UNKNOWN";
    }
}


void CshixunDefectDlg::OnBnClickedButton1()
{
    // 加载图片
    CFileDialog dlg(TRUE, L"*.bmp;*.jpg;*.png", NULL,
        OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST,
        L"图片文件|*.bmp;*.jpg;*.png|所有文件|*.*||", this);

    if (dlg.DoModal() == IDOK)
    {
        CString filePath = dlg.GetPathName();

        // 将CString转换为std::string（UTF-8）
        CT2CA filePathConverted(filePath, CP_UTF8);
        std::string input_path = filePathConverted;

        cv::Mat img = cv::imread(input_path);
        if (img.empty())
        {
            MessageBox(L"无法加载图片！", L"错误", MB_OK | MB_ICONERROR);
            return;
        }

        // 获取前景掩码
        auto [mask, ok] = get_foreground_mask(img);
        if (!ok) {
            MessageBox(L"GrabCut失败！", L"错误", MB_OK | MB_ICONERROR);
            return;
        }

        // 转换为HSV和灰度图
        cv::Mat hsv, gray;
        cv::cvtColor(img, hsv, cv::COLOR_BGR2HSV);
        cv::cvtColor(img, gray, cv::COLOR_BGR2GRAY);

        // 检测缺陷
        std::vector<DefectInfo> defects;
        std::vector<std::string> tags;

        // 凹陷检测
        if (auto defect = find_indentation_defect(img, hsv, mask)) {
            defects.push_back(*defect);
        }

        // 褐色斑点检测
        if (auto defect = find_brown_candidate(hsv, mask)) {
            defects.push_back(*defect);
        }

        // 碎片检测
        if (auto defect = find_debris_candidate(gray, mask, img.size())) {
            defects.push_back(*defect);
        }

        // 暗斑检测
        if (auto defect = find_dark_spot(hsv, mask)) {
            defects.push_back(*defect);
        }

        // 复制原图用于绘制
        cv::Mat draw_img = img.clone();

        // 如果没有检测到缺陷，标记为CLEAN
        if (defects.empty()) {
            tags.push_back("CLEAN");
            cv::putText(draw_img, "CLEAN", cv::Point(100, 100), cv::FONT_HERSHEY_SIMPLEX, 3, cv::Scalar(0, 0, 255), 10);
        }

        // 绘制缺陷
        for (const auto& defect : defects) {
            std::string type_str = defect_type_to_string(defect.type);

            // 添加到标签列表
            if (std::find(tags.begin(), tags.end(), type_str) == tags.end()) {
                tags.push_back(type_str);
            }

            if (defect.type == DefectType::INDENTATION) {
                // 绘制蓝色区域轮廓（绿色）
                cv::drawContours(draw_img, std::vector<std::vector<cv::Point>>{defect.contour},
                    -1, cv::Scalar(0, 255, 0), 2);

                // 绘制左右角点
                cv::circle(draw_img, defect.p_left, 6, cv::Scalar(0, 0, 255), -1);
                cv::circle(draw_img, defect.p_right, 6, cv::Scalar(0, 0, 255), -1);

                // 绘制连线
                cv::line(draw_img, defect.p_left, defect.p_right, cv::Scalar(0, 0, 0), 2);

                // 绘制凹痕区域矩形
                cv::rectangle(draw_img, defect.defect_rect, cv::Scalar(0, 0, 255), 2);
            }
            else {
                // 绘制普通矩形
                cv::rectangle(draw_img, defect.rect, defect.color, 2);
            }
            cv::putText(draw_img, type_str, cv::Point(100, 100), cv::FONT_HERSHEY_SIMPLEX, 3, cv::Scalar(0, 0, 255), 10);
        }
        // 将BGR转换为RGB
        cv::Mat rgbImage;
        cv::cvtColor(draw_img, rgbImage, cv::COLOR_BGR2RGB);
        // 获取图片信息
        int width = draw_img.cols;
        int height = draw_img.rows;
        int channels = draw_img.channels();
        // 释放之前的图片
        if (!m_image.IsNull())
            m_image.Destroy();
        // 创建CImage对象 - 使用32位带Alpha通道
        // 这样可以避免对齐问题，并且更容易处理颜色格式
        m_image.Create(width, height, 32);

        // 设置Alpha通道为255（完全不透明）
        for (int y = 0; y < height; y++)
        {
            BYTE* pRowCurrent = (BYTE*)m_image.GetPixelAddress(0, y);
            cv::Vec3b* rgbRow = rgbImage.ptr<cv::Vec3b>(y);

            for (int x = 0; x < width; x++)
            {
                int base = x * 4;
                pRowCurrent[base] = rgbRow[x][2];     // B
                pRowCurrent[base + 1] = rgbRow[x][1]; // G
                pRowCurrent[base + 2] = rgbRow[x][0]; // R
                pRowCurrent[base + 3] = 255;          // A
            }
        }
        // 更新显示
        Invalidate();
    }
}
