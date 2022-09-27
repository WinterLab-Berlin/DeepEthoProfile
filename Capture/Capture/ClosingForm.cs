using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Capture
{
    public partial class ClosingForm : Form
    {
        public ClosingForm()
        {
            InitializeComponent();

            FormClosing += ClosingForm_FormClosing;
        }

        private void ClosingForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if(!CanClose)
                e.Cancel = true;
        }

        public bool CanClose
        {
            get; set;
        }
    }
}
