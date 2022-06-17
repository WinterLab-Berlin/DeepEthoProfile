///author andrei.istudor@hu-berlin.de

using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Drawing;

//using Unosquare.FFME.Events;

namespace VideoAnnotationViewer
{
    enum AnnotationMode { Viewing, Manual };

    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        double[] _speedMultiplierSeries = { 0.04, 0.08, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.8, 2, 2.4, 5, 10 };
        int _crtSpeedMultiplier = 6;
        int frameRate = 0;
        double _playFrameRate = 0;

        long _crtFrameIndex = 0;
        long _totalSeconds = 0;

        string playButtonText = "Play";
        string pauseButtonText = "Pause";

        bool _exclusiveAnnotation = false;

        Dictionary<int, RadioButton> manualAnnotationsRadioBtns;
        Dictionary<int, Label> loadedAnnotationsLabels;

        AnnotationMode _annotationMode = AnnotationMode.Viewing;

        int _crtFrameAnnotation = 0;
        int _crtManualAnnotation = 0;
        AnnotationWrapper _loadedAnnotation;
        AnnotationWrapper _manualAnnotation;

        public MainWindow()
        {
            Unosquare.FFME.MediaElement.FFmpegDirectory = @"..\\..\\ffmpeg";
            InitializeComponent();

            videoControl.LoadedBehavior = MediaState.Pause;
            videoControl.MediaOpened += Media_MediaOpened;
            videoControl.RenderingVideo += Media_RenderingVideo;
            //videoControl.PositionChanged += VideoControl_PositionChanged;
        }

        //private void VideoControl_PositionChanged(object sender, Unosquare.FFME.Events.PositionChangedRoutedEventArgs e)
        //{
        //    Console.WriteLine("position changed");
        //}

        private void Media_RenderingVideo(object sender, Unosquare.FFME.Events.RenderingVideoEventArgs e)
        {
            //Console.Write(e.PictureNumber + ", time: ");
            //Console.WriteLine(e.Clock.ToString(@"hh\:mm\:ss\.fff"));

            _crtFrameIndex = e.PictureNumber;
            Bitmap crtFrame = e.Bitmap.CreateDrawingBitmap();
            //BitmapDataBuffer crtFrame = e.Bitmap;

            //Console.WriteLine("new frame changed, width = " + crtFrame.PixelWidth + ", height = " + crtFrame.PixelHeight);
            using (Graphics g = Graphics.FromImage(crtFrame))
            {
                String overlayMsg = "Frame=" + e.PictureNumber;
                overlayMsg += ", " + e.Clock.ToString(@"hh\:mm\:ss\.fff");

                if (frameRate != (int)_playFrameRate)
                    overlayMsg += ", fps=" + _playFrameRate;

                // Create point for upper-left corner of drawing.
                PointF startTextPoint = new PointF(40.0F, 12.0F);

                // Draw string to screen.
                g.DrawString(overlayMsg, new Font("Arial", 18), new SolidBrush(System.Drawing.Color.LimeGreen), startTextPoint);
            }

            //TODO: sync slider somehow
            ////settingTimeSlider = true;
            //if(!videoControl.IsPaused)
            //    frameSlider.Value = videoControl.Position.TotalSeconds;

            //TODO: load the correpsonding annotation (and overlay)
            markAnnotation(_crtFrameIndex);
        }

        private void onVideoLoaded(String videoName)
        {
            Console.WriteLine("load video file: " + videoName);

            videoFileNameLabel.Content = videoName; //loadVideoDialog.SafeFileName;

            //TODO: load the appropiate annotations automatically
            resetAnnotations(0);
            annotationFileNameLabel.Content = "";

            goToButton.IsEnabled = true;
            goToTextBox.IsEnabled = true;
            goToTextBox.Text = "0";
        }
        private void onVideoUnloaded()
        {
            goToButton.IsEnabled = false;
            goToTextBox.IsEnabled = false;
        }

        #region event handlers
        private async void loadVideoButton_Click(object sender, RoutedEventArgs e)
        {
            bool videoPlaying = videoControl.IsPlaying;
            await videoControl.Pause();

            Microsoft.Win32.OpenFileDialog loadVideoDialog = new Microsoft.Win32.OpenFileDialog();

            loadVideoDialog.DefaultExt = ".avi; mkv; mp4";
            loadVideoDialog.Filter = "Video Files (*.avi, *.mkv, *.mp4)|*.avi; *.mkv; *.mp4";
            Nullable<bool> result = loadVideoDialog.ShowDialog();

            if (result == true)
            {
                videoControl.Source = new Uri(loadVideoDialog.FileName);
                onVideoLoaded(loadVideoDialog.SafeFileName);
            }
            else
            {
                if(videoPlaying)
                    await videoControl.Play();
            }
        }

        private void Media_MediaOpened(object sender, RoutedEventArgs e)
        {
            if (videoControl.IsLoaded)
            {
                //TODO: it actually changed to ms
                if (videoControl.NaturalDuration.HasTimeSpan)
                    _totalSeconds = (int)videoControl.NaturalDuration.TimeSpan.TotalSeconds;
                else
                {
                    _totalSeconds = 1000;
                    Console.WriteLine("cannot load video length, use default - should try again");
                }

                _playFrameRate = 1.0 / videoControl.VideoFrameLength;
            }
            else
            {
                _totalSeconds = 1000;
                _playFrameRate = 25;
            }

            frameRate = (int)_playFrameRate;

            frameSlider.Maximum = _totalSeconds - 1;
            frameSlider.SmallChange = (int)_totalSeconds / 200 + 1;
            frameSlider.LargeChange = (int)_totalSeconds / 50 + 1;
            frameSlider.Visibility = Visibility.Visible;
            frameSlider.Value = 0;
            _crtFrameIndex = 0;

            noFramesLabel.Visibility = Visibility.Visible;
            noFramesLabel.Content = _totalSeconds + " seconds";

            videoRuntimeLabel.Visibility = Visibility.Visible;
            videoControlsGrid.IsEnabled = true;
            frameSlider.IsEnabled = true;
        }

        private void resetAnnotations(int annotationsCount)
        {
            manualAnnotationsGrid.Children.Clear();
            manualAnnotationsGrid.RowDefinitions.Clear();
            if (manualAnnotationsRadioBtns != null)
                manualAnnotationsRadioBtns.Clear();

            manualAnnotationsRadioBtns = new Dictionary<int, RadioButton>(annotationsCount);

            loadedAnotationsGrid.Children.Clear();
            loadedAnotationsGrid.RowDefinitions.Clear();
            if (loadedAnnotationsLabels != null)
                loadedAnnotationsLabels.Clear();

            loadedAnnotationsLabels = new Dictionary<int, Label>(annotationsCount);
        }

        private async void loadAnnotationFileButton_Click(object sender, RoutedEventArgs e)
        {
            bool videoPlaying = videoControl.IsPlaying;
            await videoControl.Pause();

            Microsoft.Win32.OpenFileDialog loadAnnotationDialog = new Microsoft.Win32.OpenFileDialog();

            loadAnnotationDialog.DefaultExt = ".csv";
            loadAnnotationDialog.Filter = "Annotation Files (*.csv)|*.csv";

            Nullable<bool> result = loadAnnotationDialog.ShowDialog();

            //TODO: this is just for 10Cage now, for other data there's some more to do
            if (result == true)
            {
                String errorMessage = "";
                _loadedAnnotation = new AnnotationWrapper();

                if (!_loadedAnnotation.parseFile(loadAnnotationDialog.FileName, out errorMessage))
                {
                    MessageBox.Show(errorMessage);
                    return;
                }

                annotationFileNameLabel.Content = loadAnnotationDialog.SafeFileName;

                Dictionary<int, string> annotationCategories = _loadedAnnotation.annotationCategories;

                //add labels in manualAnnotationsStackPanel
                if (annotationCategories.Count > 0)
                {
                    resetAnnotations(annotationCategories.Count);

                    foreach (int crtCategoryId in annotationCategories.Keys)
                    {
                        //labels are displaying values from the loaded annotation file
                        Label crtCategoryLabel = new Label();
                        crtCategoryLabel.Content = annotationCategories[crtCategoryId];
                        crtCategoryLabel.FontSize = 14;
                        crtCategoryLabel.Margin = new Thickness(3, 0, 0, 0);
                        crtCategoryLabel.Padding = new Thickness(0);
                        crtCategoryLabel.VerticalAlignment = VerticalAlignment.Center;
                        crtCategoryLabel.SetValue(Grid.RowProperty, crtCategoryId);

                        loadedAnotationsGrid.RowDefinitions.Add(new RowDefinition());

                        loadedAnotationsGrid.Children.Add(crtCategoryLabel);

                        loadedAnnotationsLabels.Add(crtCategoryId, crtCategoryLabel);

                        //radio buttons are for manual input
                        RadioButton crtCategoryRadioButton = new RadioButton();
                        crtCategoryRadioButton.Content = " " + crtCategoryId.ToString() + " : " + annotationCategories[crtCategoryId];
                        crtCategoryRadioButton.Tag = crtCategoryId;
                        crtCategoryRadioButton.FontSize = 14;
                        crtCategoryRadioButton.Margin = new Thickness(3, 0, 0, 0);
                        crtCategoryRadioButton.Padding = new Thickness(5, 0, 0, 0);
                        crtCategoryRadioButton.VerticalAlignment = VerticalAlignment.Center;
                        crtCategoryRadioButton.VerticalContentAlignment = VerticalAlignment.Center;
                        crtCategoryRadioButton.SetValue(Grid.RowProperty, crtCategoryId);

                        crtCategoryRadioButton.Checked += CrtCategoryRadioButton_Checked;
                        crtCategoryRadioButton.Unchecked += CrtCategoryRadioButton_Unchecked;

                        manualAnnotationsGrid.RowDefinitions.Add(new RowDefinition());
                        manualAnnotationsGrid.Children.Add(crtCategoryRadioButton);

                        //store a handle to the label so that it can be displayed differently
                        manualAnnotationsRadioBtns.Add(crtCategoryId, crtCategoryRadioButton);
                    }

                    //only activate the possibility to choose manual mode after loading a valid annotation file
                    annotationModePanel.IsEnabled = true;
                }
            } 
            else
            {
                if (videoPlaying)
                    await videoControl.Play();
            }
        }

        private void CrtCategoryRadioButton_Unchecked(object sender, RoutedEventArgs e)
        {
            RadioButton rb = sender as RadioButton;
            rb.FontWeight = FontWeights.Normal;
        }

        private void CrtCategoryRadioButton_Checked(object sender, RoutedEventArgs e)
        {
            RadioButton rb = sender as RadioButton;
            rb.FontWeight = FontWeights.Bold;

            if (rb != null)
            {

                string checkedAnnotation = rb.Tag.ToString();
                _crtManualAnnotation = int.Parse(checkedAnnotation);
                
                //switch (checkedAnnotation)
                Console.WriteLine("radion button checked: " + checkedAnnotation);

                if (_annotationMode == AnnotationMode.Manual)
                    markAnnotation(_crtFrameIndex);
            }
        }

        private async void nextFrameButton_Click(object sender, RoutedEventArgs e)
        {
            if(videoControl.IsPlaying)
                await videoControl.Pause();

            displayNextFrame();
        }

        private async void previousFrameButton_Click(object sender, RoutedEventArgs e)
        {
            if (videoControl.IsPlaying)
                await videoControl.Pause();

            displayPreviousFrame();
        }


        private void annotationWindow_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            switch (e.Key)
            {
                case Key.Left:
                        previousFrameButton_Click(this, new RoutedEventArgs()); e.Handled = true; break;
                //case Key.Left: Console.WriteLine("ctrl left"); e.Handled = true; break;
                case Key.Right: nextFrameButton_Click(this, new RoutedEventArgs()); e.Handled = true; break;
                case Key.Space: playVideoButton_Click(this, new RoutedEventArgs()); e.Handled = true; break;
            }
        }

        private void modifyAnnotationRadioButton_Checked(object sender, RoutedEventArgs e)
        {
            bool enterManualMode = false;

            if (_manualAnnotation == null || !_manualAnnotation.initialized || String.IsNullOrEmpty(_manualAnnotation.filename))
            {
                //prompt for saving manual annotation file
                Microsoft.Win32.SaveFileDialog saveAnnotationDialog = new Microsoft.Win32.SaveFileDialog();

                saveAnnotationDialog.DefaultExt = ".csv";
                saveAnnotationDialog.Filter = "Annotation Files (*.csv)|*.csv";
                Nullable<bool> result = saveAnnotationDialog.ShowDialog();

                if (result == true)
                {
                    _manualAnnotation = new AnnotationWrapper(_loadedAnnotation.annotationCategories, _loadedAnnotation.exclusiveAnnotation);

                    _manualAnnotation.filename = saveAnnotationDialog.FileName;
                    enterManualMode = true;
                }
                else
                {
                    e.Handled = true;
                    displayAnnotationRadioButton.IsChecked = true;
                }
            }
            else
            {
                enterManualMode = true;
            }

            if (enterManualMode)
            {
                //set manual annoation mode
                manualAnnotationsGrid.IsEnabled = true;
                _annotationMode = AnnotationMode.Manual;
            }
        }

        private void displayAnnotationRadioButton_Checked(object sender, RoutedEventArgs e)
        {
            //turn (back) to display mode
            manualAnnotationsGrid.IsEnabled = false;
            _annotationMode = AnnotationMode.Viewing;
        }

        private void playVideoButton_Click(object sender, RoutedEventArgs e)
        {
            if (videoControl.IsPaused)
            {
                playVideoButton.Content = pauseButtonText;
                //frameSlider.ValueChanged -= frameSlider_ValueChanged;
                videoControl.Play();
            }
            else
            {
                playVideoButton.Content = playButtonText;
                videoControl.Pause();
            }
        }

        #endregion

        private async void jumpFrames(long frame)
        {
            await videoControl.Pause();
            playVideoButton.Content = playButtonText;

            TimeSpan crtPos = videoControl.Position.Add(TimeSpan.FromMilliseconds(1));
            TimeSpan ts = TimeSpan.FromSeconds(frame * videoControl.VideoFrameLength);
            videoControl.Position = crtPos.Add(ts);
            _crtFrameIndex = Convert.ToInt64(videoControl.Position.TotalSeconds * videoControl.VideoFrameRate);

            Console.WriteLine("new frame is: " + _crtFrameIndex + ", new position is: " + videoControl.Position.TotalSeconds);
        }

        private async void goToFrame(long frame)
        {
            await videoControl.Pause();
            playVideoButton.Content = playButtonText;

            TimeSpan ts = TimeSpan.FromSeconds(frame * videoControl.VideoFrameLength);
            _crtFrameIndex = frame;
            videoControl.Position = ts;

            Console.WriteLine("new frame is: " + _crtFrameIndex + ", new position is: " + videoControl.Position.TotalSeconds);
        }

        private void markAnnotation(long frame)
        {
            //TODO: for exclusive annotation should be pretty different here
            if (_loadedAnnotation != null)
            {
                int frameAnnotation = _loadedAnnotation.getAnnotation(frame);
                if (_crtFrameAnnotation != frameAnnotation)
                {
                    loadedAnnotationsLabels[_crtFrameAnnotation].FontWeight = FontWeights.Normal;
                    loadedAnnotationsLabels[_crtFrameAnnotation].Foreground = System.Windows.Media.Brushes.Black;

                    loadedAnnotationsLabels[frameAnnotation].FontWeight = FontWeights.Bold;
                    loadedAnnotationsLabels[frameAnnotation].Foreground = System.Windows.Media.Brushes.Red;
                    _crtFrameAnnotation = frameAnnotation;
                }
            }

            if (_annotationMode == AnnotationMode.Manual)
            {
                if (_manualAnnotation == null || !_manualAnnotation.initialized)
                {
                    //TODO: init? it is an error actually - should never get here 
                    Console.WriteLine("manual annotation not initialized - should never get here");
                }
                else
                {
                    //take annotation and put it in 
                    if (_crtManualAnnotation > 0)
                        _manualAnnotation.addAnnotation(frame, _crtManualAnnotation);
                    else
                    {
                        int crtManualAnnotation = _manualAnnotation.getAnnotation(frame);
                        //if (crtManualAnnotation > 0)
                        {
                            manualAnnotationsRadioBtns[crtManualAnnotation].IsChecked = true;
                        }
                    }
                }
            }
            else
            {
                if (_manualAnnotation != null && _manualAnnotation.initialized)
                {
                    int crtManualAnnotation = _manualAnnotation.getAnnotation(frame);
                    manualAnnotationsRadioBtns[crtManualAnnotation].IsChecked = true;
                }
            }
        }
       
        private void displayNextFrame()
        {
            if (_crtFrameIndex < (_totalSeconds - 1) * videoControl.VideoFrameRate)
                jumpFrames(1);
        }

        private void displayPreviousFrame()
        {
            if (_crtFrameIndex > 0)
                jumpFrames(-1);
        }

        //TODO: the slider will not be updated while playing
        private async void frameSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            long jumpSeconds = (long)e.NewValue;

            await jumpToSecond(jumpSeconds);
        }

        private async Task jumpToSecond(long second)
        {
            Task tt = videoControl.Pause();
            Console.WriteLine("should pause now");
            playVideoButton.Content = playButtonText;
            await tt;

            videoControl.Position = TimeSpan.FromSeconds(second);
        }


        private void slowerButton_Click(object sender, RoutedEventArgs e)
        {
            if (_crtSpeedMultiplier > 0)
            {
                _crtSpeedMultiplier--;

                updatePlaySpeed();
            }
        }

        private void fasterButton_Click(object sender, RoutedEventArgs e)
        {
            if (_crtSpeedMultiplier < _speedMultiplierSeries.Length - 1)
            {
                _crtSpeedMultiplier++;

                updatePlaySpeed();
            }
        }

        private void updatePlaySpeed()
        {
            _playFrameRate = frameRate * _speedMultiplierSeries[_crtSpeedMultiplier];
            videoControl.SpeedRatio = _speedMultiplierSeries[_crtSpeedMultiplier];

            if (_playFrameRate > 50)
            {
                //disable manual annotation
                displayAnnotationRadioButton.IsChecked = true;
            }
        }

        private void annotationWindow_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            //TODO: save manual annotation file
            if (_manualAnnotation != null)
                _manualAnnotation.save(_loadedAnnotation);
        }

        //TODO: check a solution here for updating the slider when playing - disable event
        private async void frameSlider_PreviewMouseDown(object sender, MouseButtonEventArgs e)
        {
            //if (frameSlider.ValueChanged != frameSlider_ValueChanged)
            //    frameSlider.ValueChanged += frameSlider_ValueChanged;
        }

        private void goToButton_Click(object sender, RoutedEventArgs e)
        {
            goToFrame(goToTextBox.Text);
        }

        private void goToTextBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key.Equals(Key.Return))
                goToFrame(goToTextBox.Text);
            else if (!(e.Key >= Key.D0 && e.Key <= Key.D9) && !(e.Key >= Key.NumPad0 && e.Key <= Key.NumPad9)) 
            {
                e.Handled = true;
            }

        }

        private void goToFrame(string frameString)
        {
            long frame = -1;

            if (Int64.TryParse(frameString, out frame))
            {
                goToFrame(frame);
            }
        }
    }
}
