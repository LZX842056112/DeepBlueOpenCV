#include "pch.h"
#include "framework.h"
#include "shixun3MFC.h"
#include "shixun3MFCDlg.h"
#include "afxdialogex.h"
#include <atlimage.h>  // 添加CImage头文件
#include "init.h"
#include <chrono> // c++计时库
#include <windows.h> // Windows API



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


// Cshixun3MFCDlg 对话框



Cshixun3MFCDlg::Cshixun3MFCDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_SHIXUN3MFC_DIALOG, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void Cshixun3MFCDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Control(pDX, IDCANCEL, m_picture);
}

BEGIN_MESSAGE_MAP(Cshixun3MFCDlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_BUTTON1, &Cshixun3MFCDlg::OnBnClickedButton1)
	ON_BN_CLICKED(IDC_BUTTON2, &Cshixun3MFCDlg::OnBnClickedButton2)
	ON_BN_CLICKED(IDC_BUTTON3, &Cshixun3MFCDlg::OnBnClickedButton3)
	ON_BN_CLICKED(IDC_BUTTON4, &Cshixun3MFCDlg::OnBnClickedButton4)
	ON_BN_CLICKED(IDC_BUTTON5, &Cshixun3MFCDlg::OnBnClickedButton5)
	ON_BN_CLICKED(IDC_BUTTON6, &Cshixun3MFCDlg::OnBnClickedButton6)
	ON_BN_CLICKED(IDC_BUTTON7, &Cshixun3MFCDlg::OnBnClickedButton7)
	ON_BN_CLICKED(IDC_BUTTON8, &Cshixun3MFCDlg::OnBnClickedButton8)
	ON_BN_CLICKED(IDC_BUTTON9, &Cshixun3MFCDlg::OnBnClickedButton9)
	ON_BN_CLICKED(IDC_BUTTON10, &Cshixun3MFCDlg::OnBnClickedButton10)
	ON_BN_CLICKED(IDC_BUTTON11, &Cshixun3MFCDlg::OnBnClickedButton11)
	ON_BN_CLICKED(IDC_BUTTON12, &Cshixun3MFCDlg::OnBnClickedButton12)
	ON_BN_CLICKED(IDC_BUTTON13, &Cshixun3MFCDlg::OnBnClickedButton13)
END_MESSAGE_MAP()

// Cshixun3MFCDlg 消息处理程序

BOOL Cshixun3MFCDlg::OnInitDialog()
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

	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
}

void Cshixun3MFCDlg::OnSysCommand(UINT nID, LPARAM lParam)
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

void Cshixun3MFCDlg::OnPaint()
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
            // 获取设备上下
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
			double scaleRatio = min(widthRatio, heightRatio);  // 使用较小的比例，确保图片完全显示

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
            // 释放之前获取的设备上下文，避免资源泄漏。
			m_picture.ReleaseDC(pDC);
		}
	}
}

//当用户拖动最小化窗口时系统调用此函数取得光标
//显示。
HCURSOR Cshixun3MFCDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}

// 私有辅助函数
namespace {
	// 复制CImage数据
	void CopyCImageData(const CImage& src, CImage& dst)
	{
		int width = src.GetWidth();
		int height = src.GetHeight();
		int bpp = src.GetBPP();

		if (!dst.IsNull())
			dst.Destroy();

		dst.Create(width, height, bpp);

		HDC hdcSrc = src.GetDC();
		HDC hdcDst = dst.GetDC();
		BitBlt(hdcDst, 0, 0, width, height, hdcSrc, 0, 0, SRCCOPY);
		src.ReleaseDC();
		dst.ReleaseDC();

		// 如果是8位灰度图像，复制调色板
		if (bpp == 8)
		{
			RGBQUAD palette[256];
			src.GetColorTable(0, 256, palette);
			dst.SetColorTable(0, 256, palette);
		}
	}

	// CImage转cv::Mat
	cv::Mat CImageToMat(CImage& image)
	{
		int width = image.GetWidth();
		int height = image.GetHeight();
		int channels = image.GetBPP() / 8;

		if (channels == 1) // 灰度图像
		{
			cv::Mat mat(height, width, CV_8UC1);
			for (int y = 0; y < height; y++)
			{
				BYTE* pRow = (BYTE*)image.GetPixelAddress(0, y);
				uchar* matRow = mat.ptr<uchar>(y);
				memcpy(matRow, pRow, width);
			}
			return mat;
		}
		else if (channels >= 3) // 彩色图像
		{
			cv::Mat mat(height, width, CV_8UC3);
			for (int y = 0; y < height; y++)
			{
				BYTE* pRow = (BYTE*)image.GetPixelAddress(0, y);
				cv::Vec3b* matRow = mat.ptr<cv::Vec3b>(y);
				for (int x = 0; x < width; x++)
				{
					int base = x * channels;
					matRow[x][0] = pRow[base];     // B
					matRow[x][1] = pRow[base + 1]; // G
					matRow[x][2] = pRow[base + 2]; // R
				}
			}
			return mat;
		}
		return cv::Mat();
	}

	// cv::Mat转CImage
	void MatToCImage(const cv::Mat& mat, CImage& image)
	{
		int width = mat.cols;
		int height = mat.rows;

		if (!image.IsNull())
			image.Destroy();

		if (mat.channels() == 3) // 彩色图像
		{
			// 创建32位图像（带Alpha通道）
			image.Create(width, height, 32);

			for (int y = 0; y < height; y++)
			{
				BYTE* pRow = (BYTE*)image.GetPixelAddress(0, y);
				const cv::Vec3b* matRow = mat.ptr<cv::Vec3b>(y);
				for (int x = 0; x < width; x++)
				{
					int base = x * 4;
					pRow[base] = matRow[x][0];     // B
					pRow[base + 1] = matRow[x][1]; // G
					pRow[base + 2] = matRow[x][2]; // R
					pRow[base + 3] = 255;          // A
				}
			}
		}
		else if (mat.channels() == 1) // 灰度图像
		{
			// 创建8位灰度图像
			image.Create(width, height, 8);
			// 设置灰度调色板
			RGBQUAD palette[256];
			for (int i = 0; i < 256; i++)
			{
				palette[i].rgbRed = palette[i].rgbGreen = palette[i].rgbBlue = i;
				palette[i].rgbReserved = 0;
			}
			image.SetColorTable(0, 256, palette);
			// 复制数据
			for (int y = 0; y < height; y++)
			{
				BYTE* pRow = (BYTE*)image.GetPixelAddress(0, y);
				const uchar* matRow = mat.ptr<uchar>(y);
				memcpy(pRow, matRow, width);
			}
		}
	}

	// 处理图像操作
	bool ProcessImageOperation(CImage& image, std::function<void(cv::Mat&)> operation)
	{
		cv::Mat mat = CImageToMat(image);

		if (mat.empty())
			return false;

		operation(mat);
		MatToCImage(mat, image);
		return true;
	}
}

// 你好
void Cshixun3MFCDlg::OnBnClickedButton2()
{
	// 你好
	MessageBox(_T("你好！"), _T("提示"), MB_OK | MB_ICONINFORMATION);
}

// 加载图片
void Cshixun3MFCDlg::OnBnClickedButton1()
{
	// 文件选择对话框
	CFileDialog dlg(TRUE, L"*.bmp;*.jpg;*.png", NULL,
		OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST,
		L"图片文件|*.bmp;*.jpg;*.png|所有文件|*.*||", this);
    // 显示模态对话框，用户确认选择后继续执行
	if (dlg.DoModal() == IDOK)
	{
		if (!m_originalImage.IsNull())
			m_originalImage.Destroy();
        // 加载用户选择的图片文件
		if (m_originalImage.Load(dlg.GetPathName()) == S_OK)
		{
			// 复制CImage数据
			CopyCImageData(m_originalImage, m_image);
			// 更新显示，触发窗口重绘，使新加载的图片能够显示出来
			Invalidate();
		}
		else
		{
			MessageBox(L"图片加载失败", L"错误", MB_OK | MB_ICONERROR);
		}
	}
}

// opencv显示图片
void Cshixun3MFCDlg::OnBnClickedButton3()
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
		std::string imgPath = filePathConverted;

		// 使用OpenCV读取图片
		cv::Mat image = cv::imread(imgPath, cv::IMREAD_COLOR);

		if (image.empty())
		{
			MessageBox(L"OpenCV无法加载图片！", L"错误", MB_OK | MB_ICONERROR);
			return;
		}

		// 获取图片信息
		int width = image.cols;
		int height = image.rows;
		int channels = image.channels();

		// 使用OpenCV将BGR转换为RGB
		cv::Mat rgbImage;
		cv::cvtColor(image, rgbImage, cv::COLOR_BGR2RGB);

		// 释放之前的图片
		if (!m_originalImage.IsNull())
			m_originalImage.Destroy();
		if (!m_image.IsNull())
			m_image.Destroy();

		// 创建CImage对象 - 使用32位带Alpha通道
		// 这样可以避免对齐问题，并且更容易处理颜色格式
		m_originalImage.Create(width, height, 32);
		m_image.Create(width, height, 32);

		// 设置Alpha通道为255（完全不透明）
		for (int y = 0; y < height; y++)
		{
			BYTE* pRowOriginal = (BYTE*)m_originalImage.GetPixelAddress(0, y);
			BYTE* pRowCurrent = (BYTE*)m_image.GetPixelAddress(0, y);
			cv::Vec3b* rgbRow = rgbImage.ptr<cv::Vec3b>(y);

			for (int x = 0; x < width; x++)
			{
				int base = x * 4;
				pRowOriginal[base] = rgbRow[x][2];     // B
				pRowOriginal[base + 1] = rgbRow[x][1]; // G
				pRowOriginal[base + 2] = rgbRow[x][0]; // R
				pRowOriginal[base + 3] = 255;          // A
				memcpy(&pRowCurrent[base], &pRowOriginal[base], 4);
			}
		}

		// 更新显示
		Invalidate();
	}
}

// 膨胀
void Cshixun3MFCDlg::OnBnClickedButton4()
{
	auto start = std::chrono::steady_clock::now();
	// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}
	bool success = ProcessImageOperation(m_image, [](cv::Mat& mat) {
		cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
		cv::dilate(mat, mat, kernel);
		});

	if (success)
		Invalidate();

		auto end = std::chrono::steady_clock::now();
		// 转为毫秒
		auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
		CString msg;
		msg.Format(L"chrono 计时：%lld ms", duration);
		AfxMessageBox(msg);
}

// 腐蚀
void Cshixun3MFCDlg::OnBnClickedButton5()
{
	LARGE_INTEGER freq, start, end;
	// 获取计数器频率
	QueryPerformanceFrequency(&freq);
	QueryPerformanceCounter(&start);
	// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}
	bool success = ProcessImageOperation(m_image, [](cv::Mat& mat) {
		cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
		cv::erode(mat, mat, kernel);
		});

	if (success)
		Invalidate();

		QueryPerformanceCounter(&end);
		double time_ms = (end.QuadPart - start.QuadPart) * 1000.0 / freq.QuadPart;
		CString msg;
		msg.Format(L"Windows API 计时：%.3f ms", time_ms);
		AfxMessageBox(msg);
}

// Canney
void Cshixun3MFCDlg::OnBnClickedButton6()
{
	// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}
	bool success = ProcessImageOperation(m_image, [](cv::Mat& mat) {
		// 如果图像是彩色的，先转换为灰度
		if (mat.channels() == 3)
		{
			cv::cvtColor(mat, mat, cv::COLOR_BGR2GRAY);
		}

		// 使用Canny边缘检测
		cv::Canny(mat, mat, 50, 150);
	});

	if (success)
		Invalidate();
}

// 高斯滤波
void Cshixun3MFCDlg::OnBnClickedButton7()
{
	// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}

	bool success = ProcessImageOperation(m_image, [](cv::Mat& mat) {
		cv::GaussianBlur(mat, mat, cv::Size(5, 5), 0);
	});

	if (success)
		Invalidate();
}

// 中值滤波
void Cshixun3MFCDlg::OnBnClickedButton8()
{
	// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}
	bool success = ProcessImageOperation(m_image, [](cv::Mat& mat) {
		cv::medianBlur(mat, mat, 5);
	});

	if (success)
		Invalidate();
}

// 灰度化
void Cshixun3MFCDlg::OnBnClickedButton9()
{
	// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}

	cv::Mat mat = CImageToMat(m_image);

	if (mat.empty())
		return;

	cv::Mat grayMat;

	// 如果图像是彩色的，转换为灰度
	if (mat.channels() == 3)
	{
		cv::cvtColor(mat, grayMat, cv::COLOR_BGR2GRAY);

		// 将灰度图转换为3通道以便显示（这样可以看到灰度效果）
		cv::Mat gray3Ch;
		cv::cvtColor(grayMat, gray3Ch, cv::COLOR_GRAY2BGR);

		MatToCImage(gray3Ch, m_image);
	}
	else if (mat.channels() == 1)
	{
		// 如果已经是灰度图，转换为3通道显示
		cv::cvtColor(mat, grayMat, cv::COLOR_GRAY2BGR);
		MatToCImage(grayMat, m_image);
	}

	Invalidate();
}

// 二值化
void Cshixun3MFCDlg::OnBnClickedButton10()
{
	// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}

	cv::Mat mat = CImageToMat(m_image);

	if (mat.empty())
		return;

	cv::Mat grayMat, binaryMat;

	// 如果图像是彩色的，先转换为灰度
	if (mat.channels() == 3)
	{
		cv::cvtColor(mat, grayMat, cv::COLOR_BGR2GRAY);
	}
	else if (mat.channels() == 1)
	{
		grayMat = mat.clone();
	}
	else
	{
		MessageBox(L"不支持的图像格式！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}

	// 使用Otsu自适应阈值进行二值化
	cv::threshold(grayMat, binaryMat, 0, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);

	// 将二值图转换为3通道以便显示
	cv::Mat binary3Ch;
	cv::cvtColor(binaryMat, binary3Ch, cv::COLOR_GRAY2BGR);

	MatToCImage(binary3Ch, m_image);
	Invalidate();
}

// 基础霍夫变换
void Cshixun3MFCDlg::OnBnClickedButton11()
{
	// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}
	bool success = ProcessImageOperation(m_image, [](cv::Mat& mat) {
		// 创建彩色副本用于绘制直线
		cv::Mat colorMat;
		if (mat.channels() == 1)
		{
			cv::cvtColor(mat, colorMat, cv::COLOR_GRAY2BGR);
		}
		else
		{
			colorMat = mat.clone();
		}

		// 边缘检测
		cv::Mat edges;
		cv::Canny(mat, edges, 50, 150);

		// 霍夫变换检测直线
		std::vector<cv::Vec2f> lines;
		cv::HoughLines(edges, lines, 1, CV_PI / 180, 150);

		// 绘制检测到的直线
		for (size_t i = 0; i < lines.size(); i++)
		{
			float rho = lines[i][0];
			float theta = lines[i][1];
			double a = cos(theta);
			double b = sin(theta);
			double x0 = a * rho;
			double y0 = b * rho;
			cv::Point pt1(cvRound(x0 + 1000 * (-b)), cvRound(y0 + 1000 * (a)));
			cv::Point pt2(cvRound(x0 - 1000 * (-b)), cvRound(y0 - 1000 * (a)));
			cv::line(colorMat, pt1, pt2, cv::Scalar(0, 0, 255), 2);
		}

		mat = colorMat;
		});

	if (success)
		Invalidate();
}

//概率霍夫变换
void Cshixun3MFCDlg::OnBnClickedButton13()
{// 检查是否有图片加载
	if (m_image.IsNull())
	{
		MessageBox(L"请先加载图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}
	bool success = ProcessImageOperation(m_image, [](cv::Mat& mat) {
		// 创建彩色副本用于绘制直线
		cv::Mat colorMat;
		if (mat.channels() == 1)
		{
			cv::cvtColor(mat, colorMat, cv::COLOR_GRAY2BGR);
		}
		else
		{
			colorMat = mat.clone();
		}

		// 边缘检测
		cv::Mat edges;
		cv::Canny(mat, edges, 50, 150);

		// 概率霍夫变换检测直线
		std::vector<cv::Vec4i> lines;
		cv::HoughLinesP(edges, lines, 1, CV_PI / 180, 50, 50, 10);

		// 绘制检测到的直线
		for (size_t i = 0; i < lines.size(); i++)
		{
			cv::Vec4i l = lines[i];
			cv::line(colorMat, cv::Point(l[0], l[1]), cv::Point(l[2], l[3]),
				cv::Scalar(0, 255, 0), 2);
		}

		mat = colorMat;
		});

	if (success)
		Invalidate();
}

// 还原图片
void Cshixun3MFCDlg::OnBnClickedButton12()
{
	// 检查是否有原始图片
	if (m_originalImage.IsNull())
	{
		MessageBox(L"没有可还原的原始图片！", L"错误", MB_OK | MB_ICONERROR);
		return;
	}
	// 复制CImage数据
	CopyCImageData(m_originalImage, m_image);

	// 更新显示
	Invalidate();
}
