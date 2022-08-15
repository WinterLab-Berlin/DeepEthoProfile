///author andrei.istudor@hu-berlin.de

using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Threading.Tasks;

namespace VideoAnnotationViewer
{
    class AnnotationWrapper
    {
        public AnnotationWrapper()
        {
            _initialized = false;
        }

        public AnnotationWrapper(Dictionary<int, string> annotationCategories, bool exclusiveAnnotation)
        {
            _initialized = false;
            _exclusiveAnnotation = exclusiveAnnotation;

            if (annotationCategories != null && annotationCategories.Count > 0)
            {
                _annotationCategories = new Dictionary<int, string>(annotationCategories);
                _initialized = true;
            }
        }

        public bool parseFile(string filename, out string errMess)
        {
            if (String.IsNullOrEmpty(filename) || !File.Exists(filename))
            {
                errMess = "Annotation file does not exist: " + filename;
                return false;
            }
            else
            {
                _filename = filename;
            }

            using (StreamReader annotationsReader = File.OpenText(_filename))
            {
                //read annotations definition
                string headerLine = annotationsReader.ReadLine();

                if (String.IsNullOrEmpty(headerLine))
                {
                    errMess = "Annotation file is empty";
                    return false;
                }

                string[] chunks = headerLine.Split(';');

                if (chunks.Length < 2)
                {
                    errMess = "Invalid annotation file!\nAnnotation definition is missing";
                    return false;
                }
                else
                {
                    _annotationCategories = new Dictionary<int, string>(chunks.Length);
                }

                foreach (string s in chunks)
                {
                    string crtCategory = "";
                    if (String.IsNullOrEmpty(s))
                        continue;
                    else
                        crtCategory = s.Trim();

                    if (String.IsNullOrEmpty(crtCategory))
                        continue;

                    System.Console.WriteLine(crtCategory);
                    string[] crtAnnotation = crtCategory.Split(':');
                    if (crtAnnotation != null && crtAnnotation.Length == 2)
                    {
                        int id = 0;
                        if (int.TryParse(crtAnnotation[0], out id))
                        {
                            _annotationCategories.Add(id, crtAnnotation[1].Trim());
                        }
                        else
                        {
                            Console.WriteLine("invalid header entry: " + s);

                            errMess = "Invalid annotation file!\nWrong header entry: " + s;
                            return false;
                        }
                    }
                    else
                    {
                        Console.WriteLine("wrong annotation definition: " + s + " - skipping");
                        continue;
                        //errMess = "Invalid annotation file!\nAnnotation definition is missing - split failed: " + s;
                        //return false;
                    }
                }

                //read annotation exclusive mode 1=exclusive, 0=multiple
                headerLine = annotationsReader.ReadLine();
                if (String.IsNullOrEmpty(headerLine))
                {
                    errMess = "Annotation file ended too soon";
                    return false;
                }

                chunks = headerLine.Split(':');

                if(chunks == null || chunks.Length < 2)
                {
                    errMess = "Annotation file missing exclusivity definition";
                    return false;
                }

                int value = 0;
                if (int.TryParse(chunks[1], out value))
                {
                    if (value == 0)
                    {
                        Console.WriteLine("multiple annotations");
                        _exclusiveAnnotation = false;
                    }
                    else
                    {
                        Console.WriteLine("exclusive annotations");
                        _exclusiveAnnotation = true;
                    }
                }
                else
                {
                    errMess = "invalid header exclusive definition: " + headerLine;
                    return false;
                }

                if (_annotations != null)
                    _annotations.Clear();
                _annotations = new Dictionary<long, int>();

                while (true)
                {
                    string crtAnnotation = annotationsReader.ReadLine();

                    if (String.IsNullOrEmpty(crtAnnotation))
                        break;

                    string[] annotationParts = crtAnnotation.Split(';');

                    if (annotationParts.Length < 2)
                        continue;

                    int step = 0;
                    int annotation = 0;

                    if (int.TryParse(annotationParts[0], out step) && int.TryParse(annotationParts[1], out annotation))
                    {
                        _annotations.Add(step, annotation);
                    }
                    else
                    {
                        errMess = "invalid annotation: " + crtAnnotation;
                        continue;
                    }
                }
            }

            _initialized = true;
            errMess = "";

            return _initialized;
        }

        public int getAnnotation(long step)
        {
            if (_annotations != null && _annotations.Keys.Contains(step))
                return _annotations[step];
            else
                return 0;
        }

        public void addAnnotation(long step, int annotation)
        {
            if (_annotations == null)
                _annotations = new Dictionary<long, int>();

            if (_annotations.ContainsKey(step))
            {
                //overwrite previous annotation
                _annotations[step] = annotation;
            }
            else
            {
                _annotations.Add(step, annotation);
            }
        }

        public void removeAnnotation(int step)
        {
            if (_annotations != null && _annotations.ContainsKey(step))
            {
                _annotations.Remove(step);
            }
        }

        public bool save(AnnotationWrapper baseAnnotationData = null)
        {
            bool result = false;

            if (_annotations != null)
            {
                if (baseAnnotationData != null)
                {
                    //TODO: merge data
                    Dictionary<long, int> annotationsToSave = mergeData(baseAnnotationData);

                    result = save(annotationsToSave);
                }
                else
                {
                    result = save(_annotations);
                }
            }

            return result;
        }


        private bool save(Dictionary<long, int> annotationsToSave)
        {
            bool result = false;

            if (_annotationCategories != null && annotationsToSave != null)
            {
                using (StreamWriter fileWriter = new StreamWriter(_filename))
                {
                    //write categories first
                    foreach (int crtCatId in _annotationCategories.Keys)
                    {
                        fileWriter.Write(crtCatId + ":" + _annotationCategories[crtCatId] + "; ");
                    }

                    fileWriter.Write("\n");

                    //write exclusive mode
                    if(_exclusiveAnnotation)
                        fileWriter.WriteLine("exclusive:1");
                    else
                        fileWriter.WriteLine("exclusive:0");


                    //write 
                    foreach (long crtStep in annotationsToSave.Keys)
                    {
                        fileWriter.WriteLine(crtStep +  ";" + annotationsToSave[crtStep]);
                    }
                }
            } 

            return result;
        }

        private Dictionary<long, int> mergeData(AnnotationWrapper baseAnnotationData)
        {
            Dictionary<long, int> mergedAnnotation = baseAnnotationData.getAnnotationCopy();

            foreach (long step in _annotations.Keys)
            {
                //TODO: what to do with overwriting zero values? 

                if (mergedAnnotation.ContainsKey(step))
                    mergedAnnotation[step] = _annotations[step];
                else
                    mergedAnnotation.Add(step, _annotations[step]);
            }

            return mergedAnnotation;
        }
        
        public Dictionary<long, int> getAnnotationCopy()
        {
            Dictionary<long, int> annotationsCopy = new Dictionary<long, int>(_annotations);

            return annotationsCopy;
        }

        #region properties
        public Dictionary<int, string> annotationCategories { get { return _annotationCategories; } }
        public bool exclusiveAnnotation { get { return _exclusiveAnnotation; } }

        public string filename { get { return _filename; } set { _filename = value; } }
        public bool initialized { get { return _initialized; } }

        #endregion


        #region variables

        bool _initialized = false;
        string _filename;
        Dictionary<int, string> _annotationCategories;
        bool _exclusiveAnnotation = true;
        Dictionary<long, int> _annotations;

        #endregion
    }
}
