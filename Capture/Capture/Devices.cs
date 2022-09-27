using DirectShowLib;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Capture
{
    public sealed class Devices
    {
        private static Devices instance = new Devices();

        List<DsDevice> m_capDevices;

        public Devices()
        {
            m_capDevices = new List<DsDevice>();
            var capDevices = DsDevice.GetDevicesOfCat(FilterCategory.VideoInputDevice);
            foreach (var cap in capDevices) {
                if (cap.Name.Contains("H.264 Visual Source")) {
                    var tmp = cap.Name.Split(' ');
                    if (tmp.Length == 5)  // U4 H.264 Visual Source 01
                        m_capDevices.Add(cap);
                }
            }
            m_capDevices.Sort((x, y) => x.Name.CompareTo(y.Name));
        } // Devices()

        public DsDevice GetDevice(int index)
        {
            if (index < m_capDevices.Count && index > -1)
                return m_capDevices[index];
            else
                return null;
        } // GetDevice(index)

        public List<string> Names
        {
            get
            {
                List<string> names = new List<string>();
                foreach (var cap in m_capDevices) {
                    names.Add(cap.Name);
                }
                return names;
            }
        }

        public static Devices Instance
        {
            get
            {
                return instance;
            }
        }
    } // class Devices
}
