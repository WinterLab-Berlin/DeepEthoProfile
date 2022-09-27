using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Capture
{
    class UserPreferences
    {
        #region Constructor
        public UserPreferences()
        {
            //Load the settings
            Load();
        }
        #endregion

        private void Load()
        {
            Cam1Ind = Properties.Settings.Default.cam1;
            Cam2Ind = Properties.Settings.Default.cam2;
            Cam3Ind = Properties.Settings.Default.cam3;
            Cam4Ind = Properties.Settings.Default.cam4;
            Cam5Ind = Properties.Settings.Default.cam5;
            Cam6Ind = Properties.Settings.Default.cam6;
            Cam7Ind = Properties.Settings.Default.cam7;
            Cam8Ind = Properties.Settings.Default.cam8;
            Cam9Ind = Properties.Settings.Default.cam9;
            Cam10Ind = Properties.Settings.Default.cam10;
        }

        public void Save()
        {
            Properties.Settings.Default.cam1 = Cam1Ind;
            Properties.Settings.Default.cam2 = Cam2Ind;
            Properties.Settings.Default.cam3 = Cam3Ind;
            Properties.Settings.Default.cam4 = Cam4Ind;
            Properties.Settings.Default.cam5 = Cam5Ind;
            Properties.Settings.Default.cam6 = Cam6Ind;
            Properties.Settings.Default.cam7 = Cam7Ind;
            Properties.Settings.Default.cam8 = Cam8Ind;
            Properties.Settings.Default.cam9 = Cam9Ind;
            Properties.Settings.Default.cam10 = Cam10Ind;

            Properties.Settings.Default.Save();
        }

        #region Properties
        public int Cam1Ind
        {
            get;
            set;
        }

        public int Cam2Ind
        {
            get;
            set;
        }

        public int Cam3Ind
        {
            get;
            set;
        }

        public int Cam4Ind
        {
            get;
            set;
        }

        public int Cam5Ind
        {
            get;
            set;
        }

        public int Cam6Ind
        {
            get;
            set;
        }

        public int Cam7Ind
        {
            get;
            set;
        }

        public int Cam8Ind
        {
            get;
            set;
        }

        public int Cam9Ind
        {
            get;
            set;
        }

        public int Cam10Ind
        {
            get;
            set;
        }
        #endregion
    }
}
