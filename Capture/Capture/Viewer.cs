using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using DirectShowLib;
using System.Runtime.InteropServices;
using System.Diagnostics;
using System.Threading;

namespace Capture
{
    partial class Viewer : UserControl
    {
        #region native
        [DllImport("oleaut32.dll", CharSet = CharSet.Unicode, ExactSpelling = true)]
        public static extern int OleCreatePropertyFrame(
            IntPtr hwndOwner,
            int x,
            int y,
            [MarshalAs(UnmanagedType.LPWStr)] string lpszCaption,
            int cObjects,
            [MarshalAs(UnmanagedType.Interface, ArraySubType = UnmanagedType.IUnknown)]
            ref object ppUnk,
            int cPages,
            IntPtr lpPageClsID,
            int lcid,
            int dwReserved,
            IntPtr lpvReserved);
        #endregion

        Capturing _capture;
        int m_selectedIndex;

        public Viewer()
        {
            InitializeComponent();

            sourceCb.Resize += (sender, e) =>
            {
                if (!sourceCb.Focused)
                    sourceCb.SelectionLength = 0;
            };
        }

        internal bool Start(string folder)
        {
            if (sourceCb.SelectedIndex > -1 && !sourceCb.SelectedValue.Equals("No camera"))
            {
                int deviceNbr = sourceCb.SelectedIndex;
                IntPtr handle = viewPnl.Handle;
                Rectangle rect = viewPnl.DisplayRectangle;
                sourceCb.Enabled = false;

                Dummy.Invoke(new Action(() =>
                {
                    if (_capture != null)
                        _capture.Stop();

                    _capture = new Capturing(Devices.Instance.GetDevice(deviceNbr), handle, rect);

                    string fileName = GetFileName(folder, ViewerNbr);

                    _capture.Start(fileName);
                }));

                return true;
            }

            return false;
        }

        internal void JustStop()
        {
            if (_capture != null)
            {
                _capture.Stop();
            }
        }

        internal void JustStart(string folder)
        {
            Dummy.Invoke(new Action(() =>
            {
                if (_capture != null)
                {
                    string fileName = GetFileName(folder, ViewerNbr);
                    _capture.Start(fileName);
                }
            }));
        }

        internal void Stop()
        {
            Invoke(new Action(() =>
            {
                sourceCb.Enabled = true;
            }));
            
            Dummy.Invoke(new Action(() =>
            {
                if (_capture != null)
                {
                    _capture.Stop();
                    _capture.Dispose();
                    _capture = null;
                }
            }));
        }

        private string GetFileName(string folder, int orderNbr)
        {
            string folderName = folder + "\\" + orderNbr.ToString("00");
            if (!System.IO.Directory.Exists(folderName))
            {
                System.IO.Directory.CreateDirectory(folderName);
            }

            DateTime now = DateTime.Now;
            string fileName = string.Format("{0}{1:00}{2:00}_{3:00}{4:00}{5:00}.mkv",
                now.Year, now.Month, now.Day, now.Hour, now.Minute, now.Second);
            fileName = System.IO.Path.Combine(folderName, fileName);

            return fileName;
        }

        public void SetSourceCbData(List<string> dataSource, int selectedIndex)
        {
            sourceCb.DataSource = dataSource.ToList();
            if (selectedIndex < dataSource.Count)
                sourceCb.SelectedIndex = selectedIndex;
            else if (dataSource.Count > 0)
                sourceCb.SelectedIndex = dataSource.Count - 1;
            m_selectedIndex = sourceCb.SelectedIndex;
        }

        public int SelectedDevice
        {
            get
            {
                return sourceCb.SelectedIndex;
            }
        }

        private void propBtn_Click(object sender, EventArgs e)
        {
            Dummy.BeginInvoke(new Action(() =>
            {
                if (_capture != null && _capture.Source != null)
                {
                    DisplayPropertyPage(_capture.Source);
                }
            }));
        }

        private void DisplayPropertyPage(IBaseFilter dev)
        {
            //Get the ISpecifyPropertyPages for the filter
            ISpecifyPropertyPages pProp = dev as ISpecifyPropertyPages;
            
            int hr = 0;

            if (pProp == null)
            {
                //If the filter doesn't implement ISpecifyPropertyPages, try displaying IAMVfwCompressDialogs instead!
                IAMVfwCompressDialogs compressDialog = dev as IAMVfwCompressDialogs;
                if (compressDialog != null)
                {

                    hr = compressDialog.ShowDialog(VfwCompressDialogs.Config, IntPtr.Zero);
                    DsError.ThrowExceptionForHR(hr);
                }
                return;
            }

            //Get the name of the filter from the FilterInfo struct
            FilterInfo filterInfo;
            hr = dev.QueryFilterInfo(out filterInfo);
            DsError.ThrowExceptionForHR(hr);

            // Get the propertypages from the property bag
            DsCAUUID caGUID;
            hr = pProp.GetPages(out caGUID);
            DsError.ThrowExceptionForHR(hr);

            // Create and display the OlePropertyFrame
            object oDevice = (object)dev;
            hr = OleCreatePropertyFrame(Dummy.Handle, 0, 0, filterInfo.achName, 1, ref oDevice, caGUID.cElems, caGUID.pElems, 0, 0, IntPtr.Zero);
            DsError.ThrowExceptionForHR(hr);

            // Release COM objects
            Marshal.FreeCoTaskMem(caGUID.pElems);
            Marshal.ReleaseComObject(pProp);
            if (filterInfo.pGraph != null)
            {
                Marshal.ReleaseComObject(filterInfo.pGraph);
            }
        }

        private void viewPnl_Resize(object sender, EventArgs e)
        {
            if (Dummy != null)
            {
                var rect = viewPnl.DisplayRectangle;
                Dummy.BeginInvoke(new Action(() =>
                {
                    if (_capture != null)
                        _capture.Paint(rect);
                }));
            }
        }

        public int ViewerNbr
        {
            get; set;
        }

        public DummyForm Dummy
        {
            get; set;
        }
    }
}
