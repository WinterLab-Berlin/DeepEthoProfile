using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Capture
{
    /// <summary>
    /// Just a dummy invisible form.
    /// </summary>
    class DummyForm : Form
    {

        protected override void SetVisibleCore(bool value)
        {
            //just override here, make sure that the form will never become visible
            if (!IsHandleCreated)
            {
                CreateHandle();
            }

            value = false;
            base.SetVisibleCore(value);
        }
    }
}
