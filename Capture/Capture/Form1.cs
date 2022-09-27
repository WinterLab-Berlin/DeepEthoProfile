using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Capture
{
    public partial class Form1 : Form
    {
        Devices m_devices;
        string m_saveDir = null;
        List<Viewer> m_viewer;
        UserPreferences m_prefs;

        DummyForm dumbForm;
        Thread separateThread;
        Thread _restart;
        int m_restartTimes = 6;
        int m_curRestartInd = 0;
        bool _isCapturing = false;
        bool _hasToStop = false;
        bool _isRunning = true;
        object _lockObject = new object();

        public Form1()
        {
            InitializeComponent();

            m_prefs = new UserPreferences();

            CreateDummyForm();

            dumbForm.Invoke(new Action(() =>
            {
                m_devices = new Devices();
            }));

            var devNames = m_devices.Names;
            devNames.Add("No camera");

            m_viewer = new List<Viewer>();
            m_viewer.Add(viewer1);
            m_viewer.Add(viewer2);
            m_viewer.Add(viewer3);
            m_viewer.Add(viewer4);
            m_viewer.Add(viewer5);
            m_viewer.Add(viewer6);
            m_viewer.Add(viewer7);
            m_viewer.Add(viewer8);
            m_viewer.Add(viewer9);
            m_viewer.Add(viewer10);

            for (int i = 0; i < m_viewer.Count; i++)
            {
                m_viewer[i].Dummy = dumbForm;
                switch (i)
                {
                    case 0:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam1Ind);
                        break;
                    case 1:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam2Ind);
                        break;
                    case 2:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam3Ind);
                        break;
                    case 3:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam4Ind);
                        break;
                    case 4:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam5Ind);
                        break;
                    case 5:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam6Ind);
                        break;
                    case 6:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam7Ind);
                        break;
                    case 7:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam8Ind);
                        break;
                    case 8:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam9Ind);
                        break;
                    case 9:
                        m_viewer[i].SetSourceCbData(devNames, m_prefs.Cam10Ind);
                        break;
                    default:
                        break;
                }

            }


            _restart = new Thread(RestartThread);
            _restart.IsBackground = true;
            _restart.Start();
        }



        private void saveBtn_Click(object sender, EventArgs e)
        {
            FolderBrowserDialog fbd = new FolderBrowserDialog();
            fbd.ShowNewFolderButton = true;
            fbd.Description = "Select the folder to save videos";

            var res = fbd.ShowDialog(this);
            if (res == System.Windows.Forms.DialogResult.OK)
            {
                saveFileTb.Text = fbd.SelectedPath;
                m_saveDir = fbd.SelectedPath;
            }
        }

        private void captureBtn_Click(object sender, EventArgs e)
        {
            if (captureBtn.Text.Equals("Start"))
            {
                if (m_saveDir != null && !_isCapturing)
                {
                    for (int i = 0; i < m_viewer.Count; i++)
                    {
                        for (int j = i + 1; j < m_viewer.Count; j++)
                        {
                            if (m_viewer[i].SelectedDevice == m_viewer[j].SelectedDevice
                                && m_viewer[i].SelectedDevice < m_devices.Names.Count)
                            {
                                MessageBox.Show(this, "You have to select two different cameras.", "Information", MessageBoxButtons.OK, MessageBoxIcon.Information);

                                return;
                            }
                        }
                    }

                    foreach (var item in m_viewer)
                    {
                        item.Start(m_saveDir);
                    }
                    captureBtn.Text = "Stop";

                    m_curRestartInd = DateTime.Now.Hour / m_restartTimes;
                    _isCapturing = true;
                } else
                {
                    MessageBox.Show(this, "You have to select the folder to save the videos.", "Information", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
            } else if (captureBtn.Text.Equals("Stop"))
            {
                Monitor.Enter(_lockObject);
                _hasToStop = true;
                captureBtn.Enabled = false;
                Monitor.PulseAll(_lockObject);
                Monitor.Exit(_lockObject);
            }
        }

        private void RestartThread()
        {
            while (_isRunning)
            {
                Monitor.Enter(_lockObject);
                if (_hasToStop)
                {
                    Parallel.For(0, m_viewer.Count, i =>
                    {
                        m_viewer[i].Stop();
                    });

                    GC.Collect();
                    GC.WaitForPendingFinalizers();

                    Invoke(new Action(() =>
                    {
                        captureBtn.Text = "Start";
                        captureBtn.Enabled = true;
                    }));

                    _isCapturing = false;
                    _hasToStop = false;
                }

                if (_isCapturing)
                {
                    int ind = DateTime.Now.Hour / m_restartTimes;

                    if (ind != m_curRestartInd)
                    {
                        Invoke(new Action(() =>
                        {
                            captureBtn.Enabled = false;
                            captureBtn.Text = "stop all";
                        }));
                        Parallel.For(0, m_viewer.Count, i =>
                        {
                            m_viewer[i].JustStop();
                        });

                        GC.Collect();
                        GC.WaitForPendingFinalizers();

                        for (int i = 0; i < m_viewer.Count; i++)
                        {
                            Invoke(new Action(() =>
                            {
                                captureBtn.Enabled = false;
                                captureBtn.Text = "start " + (i + 1);
                            }));

                            m_viewer[i].JustStart(m_saveDir);
                        }

                        Invoke(new Action(() =>
                        {
                            captureBtn.Text = "Stop";
                            captureBtn.Enabled = true;
                        }));

                        m_curRestartInd = ind;
                    }
                }
                Monitor.PulseAll(_lockObject);
                Monitor.Exit(_lockObject);

                Thread.Sleep(1000);
            }
        }

        private void CreateDummyForm()
        {
            ManualResetEvent reset = new ManualResetEvent(false);

            //create our thread
            separateThread = new Thread((ThreadStart)
            delegate
            {
                //we need a dummy form to invoke on
                dumbForm = new DummyForm();

                //signal the calling method that it can continue
                reset.Set();

                //now kick off the message loop
                Application.Run(dumbForm);
            });

            //set the apartment state of this new thread to MTA
            separateThread.SetApartmentState(ApartmentState.MTA);
            separateThread.IsBackground = true;
            separateThread.Start();

            //we need to wait for the windowing thread to have initialised before we can 
            //say that initialisation is finished
            reset.WaitOne();

            //wait for the form handle to be created, since this won't happen until the form
            //loads inside Application.Run
            while (!dumbForm.IsHandleCreated)
            {
                Thread.Sleep(0);
            }

        }

        private async void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (_isCapturing)
            {
                e.Cancel = true;

                var res = MessageBox.Show("Recording is in progress. Do you want to stop it?", "Close", MessageBoxButtons.YesNo);
                if (res == DialogResult.Yes)
                {
                    captureBtn.Text = "stoping";
                    captureBtn.Enabled = false;

                    SaveCamProps();

                    ClosingForm cf = new ClosingForm();
                    cf.CanClose = false;
                    cf.Shown += async (object cfSender, EventArgs cfE) =>
                    {
                        await Task.Run(() =>
                        {
                            Monitor.Enter(_lockObject);
                            _isCapturing = false;
                            _isRunning = false;
                            _hasToStop = false;
                            Monitor.PulseAll(_lockObject);
                            Monitor.Exit(_lockObject);

                            Parallel.For(0, m_viewer.Count, i =>
                            {
                                m_viewer[i].Stop();
                            });

                            //Thread.Sleep(10000);
                            Debug.WriteLine("ende");
                        });

                        cf.CanClose = true;
                        cf.Close();
                    };
                    cf.ShowDialog();
                    
                    this.Close();
                }
            } else
            {
                SaveCamProps();
            }
        }

        private void SaveCamProps()
        {
            for (int i = 0; i < m_viewer.Count; i++)
            {
                switch (i)
                {
                    case 0:
                        m_prefs.Cam1Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 1:
                        m_prefs.Cam2Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 2:
                        m_prefs.Cam3Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 3:
                        m_prefs.Cam4Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 4:
                        m_prefs.Cam5Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 5:
                        m_prefs.Cam6Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 6:
                        m_prefs.Cam7Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 7:
                        m_prefs.Cam8Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 8:
                        m_prefs.Cam9Ind = m_viewer[i].SelectedDevice;
                        break;
                    case 9:
                        m_prefs.Cam10Ind = m_viewer[i].SelectedDevice;
                        break;
                    default:
                        break;
                }
            }
            m_prefs.Save();
        }
    }
}
