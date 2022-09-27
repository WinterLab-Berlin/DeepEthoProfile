using DirectShowLib;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Capture
{
    public class Capturing : IDisposable
    {
        [DllImport("ole32.dll")]
        public static extern int CreateBindCtx(int reserved, out IBindCtx ppbc);

        IGraphBuilder graphBuilder;
        IVMRWindowlessControl9 m_wCtl;
        IMediaControl mediaControl;
        IMediaEvent mediaEvent;

        IBaseFilter source;
        IFileSinkFilter pFilewriter3_sink;

        DsDevice m_device;

        Guid SolveigMatroskaMuxer = new Guid("{E4B7FAF9-9CFF-4FD5-AC16-0F250F5F97B7}");
        Guid SolveigFileWriter = new Guid("{4C8D7D7E-A543-456A-A108-76989D10EB0F}");
        Guid GdclMP4Muxer = new Guid("{5FD85181-E542-4E52-8D9D-5D613C30131B}");

        public Capturing(DsDevice device, IntPtr viewBox, System.Drawing.Rectangle viewBoxRect)
        {
            m_device = device;
            SetupGraph(viewBox, viewBoxRect);
        }

        private void SetupGraph(IntPtr viewBox, System.Drawing.Rectangle viewBoxRect)
        {
            int hr = 0;

            graphBuilder = (IGraphBuilder)new FilterGraph();

            // graph builder
            ICaptureGraphBuilder2 pBuilder = (ICaptureGraphBuilder2)new CaptureGraphBuilder2();
            hr = pBuilder.SetFiltergraph(graphBuilder);
            checkHR(hr, "Can't SetFiltergraph");

            source = SetupDevice(m_device);
            hr = graphBuilder.AddFilter(source, m_device.Name);
            checkHR(hr, string.Format("Can't add {0} to graph", m_device.Name));

            AMMediaType pmt = GetMediaFormat();
            hr = ((IAMStreamConfig)GetPin(source, "Formatted")).SetFormat(pmt);
            DsUtils.FreeAMMediaType(pmt);
            checkHR(hr, "Can't set format");

            // Create Video Mixing Renderer
            IBaseFilter pVMR = (IBaseFilter)new VideoMixingRenderer9();

            // Get VMR Config interface
            IVMRFilterConfig9 config = (IVMRFilterConfig9)pVMR;
            // Set VMR mode to windowless
            config.SetRenderingMode(VMR9Mode.Windowless);
            config.SetNumberOfStreams(2);

            // Get the windowles control
            m_wCtl = (IVMRWindowlessControl9)pVMR;

            // Set the VMR clipping window
            m_wCtl.SetVideoClippingWindow(viewBox);
            m_wCtl.SetVideoPosition(null, new DsRect(viewBoxRect));

            hr = graphBuilder.AddFilter(pVMR, "Video Renderer");
            checkHR(hr, "Can't add Video Renderer to graph");

            hr = graphBuilder.ConnectDirect(GetPin(source, "Formatted"), GetPin(pVMR, "VMR Input0"), null);
            checkHR(hr, string.Format("Can't connect {0} and Video Renderer", m_device.Name));

            mediaControl = (IMediaControl)graphBuilder;
            IMediaEventEx mediaEventEx = (IMediaEventEx)graphBuilder;

            mediaEvent = (IMediaEvent)graphBuilder;

            #region avi
            // add muxer
            //IBaseFilter pAviMux = (IBaseFilter)new AviDest();
            //hr = graphBuilder.AddFilter(pAviMux, "AVI Mux");
            //checkHR(hr, "Can't add AVI Mux to graph");

            IBaseFilter pSolveigMux = (IBaseFilter)Activator.CreateInstance(Type.GetTypeFromCLSID(SolveigMatroskaMuxer));
            hr = graphBuilder.AddFilter(pSolveigMux, "MKV Mux");
            checkHR(hr, "Can't add MKV Mux to graph");

            //IBaseFilter gdclMux = (IBaseFilter)Activator.CreateInstance(Type.GetTypeFromCLSID(GdclMP4Muxer));
            //hr = graphBuilder.AddFilter(gdclMux, "MKV Mux");
            //checkHR(hr, "Can't add MKV Mux to graph");

            // add File writer
            //IBaseFilter pFileWriter3 = (IBaseFilter)new FileWriter();
            IBaseFilter pFileWriter3 = (IBaseFilter)Activator.CreateInstance(Type.GetTypeFromCLSID(SolveigFileWriter));
            hr = graphBuilder.AddFilter(pFileWriter3, "File writer");
            checkHR(hr, "Can't add File writer to graph");
            // set destination filename
            pFilewriter3_sink = pFileWriter3 as IFileSinkFilter;
            if (pFilewriter3_sink == null)
                checkHR(unchecked((int)0x80004002), "Can't get IFileSinkFilter");
            string tmp = System.IO.Path.GetTempPath();
            hr = pFilewriter3_sink.SetFileName(tmp + "sample.mkv", null);
            checkHR(hr, "Can't set filename");

            // connect AVI Mux and File writer
            //hr = graphBuilder.ConnectDirect(GetPin(pAviMux, "AVI Out"), GetPin(pFileWriter3, "in"), null);
            hr = graphBuilder.ConnectDirect(GetPin(pSolveigMux, "Out"), GetPin(pFileWriter3, "Input"), null);
            //hr = graphBuilder.ConnectDirect(GetPin(gdclMux, "Output"), GetPin(pFileWriter3, "in"), null);
            checkHR(hr, "Can't connect AVI Mux and File writer");

            // connect U4 H.264 Visual Source 00 and AVI Mux
            //hr = graphBuilder.ConnectDirect(GetPin(source, "Encoded"), GetPin(pAviMux, "Input 01"), null);
            hr = graphBuilder.ConnectDirect(GetPin(source, "Encoded"), GetPin(pSolveigMux, "In 0"), null);
            //hr = graphBuilder.ConnectDirect(GetPin(source, "Encoded"), GetPin(gdclMux, "Input 1"), null);
            checkHR(hr, "Can't connect U4 H.264 Visual Source 00 and AVI Mux");
            #endregion
        }

        public void Start(string fileName)
        {
            int hr = pFilewriter3_sink.SetFileName(fileName, null);
            checkHR(hr, "Can't set filename");

            hr = mediaControl.Run();
            DsError.ThrowExceptionForHR(hr);
        } // Start(device, handle)

        public void Stop()
        {
            if (mediaControl != null)
            {
                mediaControl.Stop();
                //mediaControl.StopWhenReady();
            }
        }

        public void Paint(System.Drawing.Rectangle viewBoxRect)
        {
            if (mediaControl != null)
            {
                //System.Drawing.Graphics gr = m_pBox.CreateGraphics();
                //IntPtr hdc = gr.GetHdc();
                //m_wCtl.RepaintVideo(m_pBox.Handle, hdc);
                //gr.ReleaseHdc(hdc);
                m_wCtl.SetVideoPosition(null, new DsRect(viewBoxRect));
            }
        }

        private AMMediaType GetMediaFormat()
        {
            AMMediaType pmt = new AMMediaType();
            pmt.majorType = MediaType.Video;
            pmt.subType = MediaSubType.RGB32;
            pmt.formatType = FormatType.VideoInfo;
            pmt.fixedSizeSamples = true;
            pmt.formatSize = 88;
            pmt.sampleSize = 1622016;
            pmt.temporalCompression = false;
            VideoInfoHeader format = new VideoInfoHeader();
            format.SrcRect = new DsRect();
            format.SrcRect.right = 704;
            format.SrcRect.bottom = 576;
            format.TargetRect = new DsRect();
            format.BitRate = 324403200;
            format.AvgTimePerFrame = 400000;
            format.BmiHeader = new BitmapInfoHeader();
            format.BmiHeader.Size = 40;
            format.BmiHeader.Width = 704;
            format.BmiHeader.Height = 576;
            format.BmiHeader.Planes = 1;
            format.BmiHeader.BitCount = 32;
            format.BmiHeader.ImageSize = 1622016;

            pmt.formatPtr = Marshal.AllocCoTaskMem(Marshal.SizeOf(format));
            Marshal.StructureToPtr(format, pmt.formatPtr, false);

            return pmt;
        }

        public IBaseFilter SetupDevice(DsDevice device)
        {
            int hr = 0;

            IBaseFilter filter = null;
            IBindCtx bindCtx = null;
            try {
                hr = CreateBindCtx(0, out bindCtx);
                DsError.ThrowExceptionForHR(hr);
                Guid guid = typeof(IBaseFilter).GUID;
                object obj;
                device.Mon.BindToObject(bindCtx, null, ref guid, out obj);
                filter = (IBaseFilter)obj;

                IAMAnalogVideoDecoder decoder = filter as IAMAnalogVideoDecoder;
                if (decoder != null) {
                    AnalogVideoStandard oldStandard;
                    decoder.get_TVFormat(out oldStandard);
                    if (oldStandard != AnalogVideoStandard.PAL_D) {
                        decoder.put_TVFormat(AnalogVideoStandard.PAL_D);
                        
                    }
                    decoder = null;
                }
            } finally {
                if (bindCtx != null)
                    Marshal.ReleaseComObject(bindCtx);
            }

            return filter;
        } // SetupDevice(device)

        IPin GetPin(IBaseFilter filter, string pinName)
        {
            IEnumPins epins;
            int hr = filter.EnumPins(out epins);
            checkHR(hr, "Can't enumerate pins");
            IntPtr fetched = Marshal.AllocCoTaskMem(4);
            IPin[] pins = new IPin[1];
            while (epins.Next(1, pins, fetched) == 0) {
                PinInfo pinInfo;
                pins[0].QueryPinInfo(out pinInfo);
                bool found = (pinInfo.name == pinName);
                DsUtils.FreePinInfo(pinInfo);
                if (found)
                    return pins[0];
            }

            checkHR(-1, "Pin not found");
            return null;
        }

        void checkHR(int hr, string msg)
        {
            if (hr < 0) {
                Debug.WriteLine(msg);
                DsError.ThrowExceptionForHR(hr);
            }
        } // checkHR(hr, msg)

        #region Properties
        public IBaseFilter Source
        {
            get
            {
                return source;
            }
        } // Source1
        #endregion

        public void Dispose()
        {
            Marshal.ReleaseComObject(mediaControl);
            mediaControl = null;
            Marshal.ReleaseComObject(mediaEvent);
            mediaEvent = null;
            Marshal.ReleaseComObject(m_wCtl);
            m_wCtl = null;
            Marshal.ReleaseComObject(graphBuilder);
            graphBuilder = null;
            Marshal.ReleaseComObject(source);
            source = null;
            Marshal.ReleaseComObject(pFilewriter3_sink);
            pFilewriter3_sink = null;
        } // Dispose()
    } // class Capture
}
