namespace Capture
{
    partial class Viewer
    {
        /// <summary> 
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary> 
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null)) {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Component Designer generated code

        /// <summary> 
        /// Required method for Designer support - do not modify 
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.sourceNameLbl = new System.Windows.Forms.Label();
            this.sourceCb = new System.Windows.Forms.ComboBox();
            this.propBtn = new System.Windows.Forms.Button();
            this.viewPnl = new System.Windows.Forms.Panel();
            this.SuspendLayout();
            // 
            // sourceNameLbl
            // 
            this.sourceNameLbl.AutoSize = true;
            this.sourceNameLbl.Location = new System.Drawing.Point(3, 8);
            this.sourceNameLbl.Name = "sourceNameLbl";
            this.sourceNameLbl.Size = new System.Drawing.Size(44, 13);
            this.sourceNameLbl.TabIndex = 4;
            this.sourceNameLbl.Text = "Source:";
            // 
            // sourceCb
            // 
            this.sourceCb.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.sourceCb.FormattingEnabled = true;
            this.sourceCb.Location = new System.Drawing.Point(60, 5);
            this.sourceCb.Name = "sourceCb";
            this.sourceCb.Size = new System.Drawing.Size(106, 21);
            this.sourceCb.TabIndex = 2;
            // 
            // propBtn
            // 
            this.propBtn.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.propBtn.Location = new System.Drawing.Point(172, 3);
            this.propBtn.Name = "propBtn";
            this.propBtn.Size = new System.Drawing.Size(75, 23);
            this.propBtn.TabIndex = 1;
            this.propBtn.Text = "Properties";
            this.propBtn.UseVisualStyleBackColor = true;
            this.propBtn.Click += new System.EventHandler(this.propBtn_Click);
            // 
            // viewPnl
            // 
            this.viewPnl.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewPnl.BackColor = System.Drawing.Color.DimGray;
            this.viewPnl.Location = new System.Drawing.Point(3, 32);
            this.viewPnl.Name = "viewPnl";
            this.viewPnl.Size = new System.Drawing.Size(247, 218);
            this.viewPnl.TabIndex = 14;
            this.viewPnl.Resize += new System.EventHandler(this.viewPnl_Resize);
            // 
            // Viewer
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.viewPnl);
            this.Controls.Add(this.propBtn);
            this.Controls.Add(this.sourceCb);
            this.Controls.Add(this.sourceNameLbl);
            this.MinimumSize = new System.Drawing.Size(250, 250);
            this.Name = "Viewer";
            this.Size = new System.Drawing.Size(250, 250);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label sourceNameLbl;
        private System.Windows.Forms.ComboBox sourceCb;
        private System.Windows.Forms.Button propBtn;
        private System.Windows.Forms.Panel viewPnl;
    }
}
