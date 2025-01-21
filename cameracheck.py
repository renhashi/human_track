import itertools
import cv2

app_ids = [
    # (cv2.CAP_ANY, 'CAP_ANY'),
    (cv2.CAP_DSHOW, 'CAP_DSHOW'),
    (cv2.CAP_MSMF, 'CAP_MSMF'),
    (cv2.CAP_V4L2, 'CAP_V4L2'),
]
fourcc_list = [
    (cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 'MJPG'),
    (cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'), 'YUYV'),
    (cv2.VideoWriter_fourcc('Y', 'U', 'Y', '2'), 'YUY2'),
    (cv2.VideoWriter_fourcc('H', '2', '6', '4'), 'H264'),
    (cv2.VideoWriter_fourcc('B', 'G', 'R', '3'), 'BGR3'),
]
frame_list = [(1920, 1080), (1280, 1024), (1280, 720), (800, 600), (640, 480)]
fps_list = [60, 30, 24, 20, 15, 10, 5, 2, 1]

# DeviceID(0～9)と、API設定の組み合わせで繰り返し
for dev_id, api_id in itertools.product(range(10), app_ids):
    # VideoCaptureオブジェクトの取得
    cap = cv2.VideoCapture(dev_id, api_id[0])
    # 無効な場合はskip
    ret = cap.isOpened()
    if ret is False:
        continue

    # VideoCaptureの情報出力
    backend = cap.getBackendName()
    print("Camera #%d (%s : %s) :" % (dev_id, api_id[1], backend))

    # 対応FOURCCの確認
    for fourcc in fourcc_list:
        cap.set(cv2.CAP_PROP_FOURCC, fourcc[0])
        ret_fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        if fourcc[0] != ret_fourcc:
            continue    # 設定失敗のためSkip

        # 対応解像度の確認
        for frame in frame_list:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame[1])
            ret_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            ret_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if frame[0] != ret_w or frame[1] != ret_h:
                continue

            # 対応FPSの確認
            for fps in fps_list:
                cap.set(cv2.CAP_PROP_FPS, fps)
                ret_fps = int(cap.get(cv2.CAP_PROP_FPS) + 0.5)
                if fps != ret_fps:
                    continue

                # プロパティの出力
                print('  Frame: %4d x %4d , FPS: %3d , FourCC: %s' % 
                        (ret_w, ret_h, ret_fps, fourcc[1]))
