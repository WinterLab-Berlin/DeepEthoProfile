namespace Capture
{
    partial class Form1
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

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.label1 = new System.Windows.Forms.Label();
            this.saveFileTb = new System.Windows.Forms.TextBox();
            this.saveBtn = new System.Windows.Forms.Button();
            this.tableLayoutPanel1 = new System.Windows.Forms.TableLayoutPanel();
            this.viewer10 = new Capture.Viewer();
            this.viewer9 = new Capture.Viewer();
            this.viewer8 = new Capture.Viewer();
            this.viewer7 = new Capture.Viewer();
            this.viewer6 = new Capture.Viewer();
            this.viewer5 = new Capture.Viewer();
            this.viewer4 = new Capture.Viewer();
            this.viewer3 = new Capture.Viewer();
            this.viewer2 = new Capture.Viewer();
            this.viewer1 = new Capture.Viewer();
            this.captureBtn = new System.Windows.Forms.Button();
            this.tableLayoutPanel1.SuspendLayout();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 15);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(78, 13);
            this.label1.TabIndex = 1;
            this.label1.Text = "Save directory:";
            // 
            // saveFileTb
            // 
            this.saveFileTb.Enabled = false;
            this.saveFileTb.Location = new System.Drawing.Point(96, 12);
            this.saveFileTb.MinimumSize = new System.Drawing.Size(138, 20);
            this.saveFileTb.Name = "saveFileTb";
            this.saveFileTb.Size = new System.Drawing.Size(383, 20);
            this.saveFileTb.TabIndex = 2;
            // 
            // saveBtn
            // 
            this.saveBtn.Location = new System.Drawing.Point(485, 10);
            this.saveBtn.Name = "saveBtn";
            this.saveBtn.Size = new System.Drawing.Size(25, 23);
            this.saveBtn.TabIndex = 3;
            this.saveBtn.Text = "...";
            this.saveBtn.UseVisualStyleBackColor = true;
            this.saveBtn.Click += new System.EventHandler(this.saveBtn_Click);
            // 
            // tableLayoutPanel1
            // 
            this.tableLayoutPanel1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.tableLayoutPanel1.ColumnCount = 4;
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25F));
            this.tableLayoutPanel1.ColumnStyles.Add(new System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 25F));
            this.tableLayoutPanel1.Controls.Add(this.viewer10, 1, 2);
            this.tableLayoutPanel1.Controls.Add(this.viewer9, 0, 2);
            this.tableLayoutPanel1.Controls.Add(this.viewer8, 3, 1);
            this.tableLayoutPanel1.Controls.Add(this.viewer7, 2, 1);
            this.tableLayoutPanel1.Controls.Add(this.viewer6, 1, 1);
            this.tableLayoutPanel1.Controls.Add(this.viewer5, 0, 1);
            this.tableLayoutPanel1.Controls.Add(this.viewer4, 3, 0);
            this.tableLayoutPanel1.Controls.Add(this.viewer3, 2, 0);
            this.tableLayoutPanel1.Controls.Add(this.viewer2, 1, 0);
            this.tableLayoutPanel1.Controls.Add(this.viewer1, 0, 0);
            this.tableLayoutPanel1.Location = new System.Drawing.Point(12, 38);
            this.tableLayoutPanel1.Name = "tableLayoutPanel1";
            this.tableLayoutPanel1.RowCount = 3;
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 33.33333F));
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 33.33334F));
            this.tableLayoutPanel1.RowStyles.Add(new System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 33.33334F));
            this.tableLayoutPanel1.Size = new System.Drawing.Size(1015, 781);
            this.tableLayoutPanel1.TabIndex = 5;
            // 
            // viewer10
            // 
            this.viewer10.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer10.Dummy = null;
            this.viewer10.Location = new System.Drawing.Point(256, 523);
            this.viewer10.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer10.Name = "viewer10";
            this.viewer10.Size = new System.Drawing.Size(250, 255);
            this.viewer10.TabIndex = 9;
            this.viewer10.ViewerNbr = 10;
            // 
            // viewer9
            // 
            this.viewer9.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer9.Dummy = null;
            this.viewer9.Location = new System.Drawing.Point(3, 523);
            this.viewer9.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer9.Name = "viewer9";
            this.viewer9.Size = new System.Drawing.Size(250, 255);
            this.viewer9.TabIndex = 8;
            this.viewer9.ViewerNbr = 9;
            // 
            // viewer8
            // 
            this.viewer8.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer8.Dummy = null;
            this.viewer8.Location = new System.Drawing.Point(762, 263);
            this.viewer8.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer8.Name = "viewer8";
            this.viewer8.Size = new System.Drawing.Size(250, 254);
            this.viewer8.TabIndex = 7;
            this.viewer8.ViewerNbr = 8;
            // 
            // viewer7
            // 
            this.viewer7.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer7.Dummy = null;
            this.viewer7.Location = new System.Drawing.Point(509, 263);
            this.viewer7.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer7.Name = "viewer7";
            this.viewer7.Size = new System.Drawing.Size(250, 254);
            this.viewer7.TabIndex = 6;
            this.viewer7.ViewerNbr = 7;
            // 
            // viewer6
            // 
            this.viewer6.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer6.Dummy = null;
            this.viewer6.Location = new System.Drawing.Point(256, 263);
            this.viewer6.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer6.Name = "viewer6";
            this.viewer6.Size = new System.Drawing.Size(250, 254);
            this.viewer6.TabIndex = 5;
            this.viewer6.ViewerNbr = 6;
            // 
            // viewer5
            // 
            this.viewer5.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer5.Dummy = null;
            this.viewer5.Location = new System.Drawing.Point(3, 263);
            this.viewer5.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer5.Name = "viewer5";
            this.viewer5.Size = new System.Drawing.Size(250, 254);
            this.viewer5.TabIndex = 4;
            this.viewer5.ViewerNbr = 5;
            // 
            // viewer4
            // 
            this.viewer4.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer4.Dummy = null;
            this.viewer4.Location = new System.Drawing.Point(762, 3);
            this.viewer4.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer4.Name = "viewer4";
            this.viewer4.Size = new System.Drawing.Size(250, 254);
            this.viewer4.TabIndex = 3;
            this.viewer4.ViewerNbr = 4;
            // 
            // viewer3
            // 
            this.viewer3.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer3.Dummy = null;
            this.viewer3.Location = new System.Drawing.Point(509, 3);
            this.viewer3.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer3.Name = "viewer3";
            this.viewer3.Size = new System.Drawing.Size(250, 254);
            this.viewer3.TabIndex = 2;
            this.viewer3.ViewerNbr = 3;
            // 
            // viewer2
            // 
            this.viewer2.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer2.Dummy = null;
            this.viewer2.Location = new System.Drawing.Point(256, 3);
            this.viewer2.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer2.Name = "viewer2";
            this.viewer2.Size = new System.Drawing.Size(250, 254);
            this.viewer2.TabIndex = 1;
            this.viewer2.ViewerNbr = 2;
            // 
            // viewer1
            // 
            this.viewer1.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.viewer1.Dummy = null;
            this.viewer1.Location = new System.Drawing.Point(3, 3);
            this.viewer1.MinimumSize = new System.Drawing.Size(250, 250);
            this.viewer1.Name = "viewer1";
            this.viewer1.Size = new System.Drawing.Size(250, 254);
            this.viewer1.TabIndex = 0;
            this.viewer1.ViewerNbr = 1;
            // 
            // captureBtn
            // 
            this.captureBtn.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.captureBtn.Location = new System.Drawing.Point(952, 9);
            this.captureBtn.Name = "captureBtn";
            this.captureBtn.Size = new System.Drawing.Size(75, 23);
            this.captureBtn.TabIndex = 6;
            this.captureBtn.Text = "Start";
            this.captureBtn.UseVisualStyleBackColor = true;
            this.captureBtn.Click += new System.EventHandler(this.captureBtn_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1039, 831);
            this.Controls.Add(this.captureBtn);
            this.Controls.Add(this.tableLayoutPanel1);
            this.Controls.Add(this.saveBtn);
            this.Controls.Add(this.saveFileTb);
            this.Controls.Add(this.label1);
            this.MinimumSize = new System.Drawing.Size(1055, 870);
            this.Name = "Form1";
            this.Text = "Capture";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.Form1_FormClosing);
            this.tableLayoutPanel1.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox saveFileTb;
        private System.Windows.Forms.Button saveBtn;
        private System.Windows.Forms.TableLayoutPanel tableLayoutPanel1;
        private Viewer viewer1;
        private Viewer viewer10;
        private Viewer viewer9;
        private Viewer viewer8;
        private Viewer viewer7;
        private Viewer viewer6;
        private Viewer viewer5;
        private Viewer viewer4;
        private Viewer viewer3;
        private Viewer viewer2;
        private System.Windows.Forms.Button captureBtn;
    }
}

