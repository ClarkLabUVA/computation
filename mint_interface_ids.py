#© 2020 By The Rector And Visitors Of The University Of Virginia

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import requests,json
interfaces = [{
  "interface":"nipype.interfaces.fsl.preprocess.MCFLIRT",
  "name":"FSL MCFLIRT",
  "description":"MCFLIRT is an intra-modal motion correction tool designed for use on fMRI time series and based on optimization and registration techniques used in FLIRT, a fully automated robust and accurate tool for linear (affine) inter- and inter-modal brain image registration.",
  "citation":"Jenkinson, M., Bannister, P., Brady, J. M. and Smith, S. M. Improved Optimisation for the Robust and Accurate Linear Registration and MotionCorrection of Brain Images. NeuroImage, 17(2), 825-841, 2002.",
},
{
  "interface":"nipype.interfaces.io.SelectFiles",
  "name":"IO SelectFiles",
  "description":"This interface uses Python's {}-based string formatting syntax to plug values (possibly known only at workflow execution time) into string templates and collect files from persistant storage.",
},
{
  "interface":"nipype.interfaces.fsl.utils.ExtractROI",
  "name":"FSL ExtractROI",
  "description":"extract region of interest (ROI) from an image. You can a) take a 3D ROI from a 3D data set (or if it is 4D, the same ROI is taken from each time point and a new 4D data set is created), b) extract just some time points from a 4D data set, or c) control time and space limits to the ROI. Note that the arguments are minimum index and size (not maximum index). So to extract voxels 10 to 12 inclusive you would specify 10 and 3 (not 10 and 12).",
  "citation":"M.W. Woolrich, S. Jbabdi, B. Patenaude, M. Chappell, S. Makni, T. Behrens, C. Beckmann, M. Jenkinson, S.M. Smith. Bayesian analysis of neuroimaging data in FSL. NeuroImage, 45:S173-86, 2009",
},
{
  "interface":"nipype.interfaces.fsl.preprocess.SliceTimer",
  "name":"FSL SliceTimer",
  "description":"slicetimer is a pre-processing tool designed to correct for sampling offsets inherent in slice-wise EPI acquisition sequences.",
},
{
  "interface":"nipype.algorithms.rapidart.ArtifactDetect",
  "name":"Algorithm ArtifactDetect",
  "description":"ArtifactDetect: performs artifact detection on functional images",
},
{
  "interface":"nipype.interfaces.fsl.preprocess.BET",
  "name":"FSL BET",
  "description":"BET (Brain Extraction Tool) deletes non-brain tissue from an image of the whole head. It can also estimate the inner and outer skull surfaces, and outer scalp surface, if you have good quality T1 and T2 input images.",
  "citation":"S.M. Smith. Fast robust automated brain extraction. Human Brain Mapping, 17(3):143-155, November 2002.",
},
{
  "interface":"nipype.interfaces.fsl.preprocess.FLIRT",
  "name":"FSL FLIRT",
  "description":"FLIRT (FMRIB's Linear Image Registration Tool) is a fully automated robust and accurate tool for linear (affine) intra- and inter-modal brain image registration.",
  "citation":["M. Jenkinson and S.M. Smith. A global optimisation method for robust affine registration of brain images. Medical Image Analysis, 5(2):143-156, 2001.","M. Jenkinson, P.R. Bannister, J.M. Brady, and S.M. Smith. Improved optimisation for the robust and accurate linear registration and motion correction of brain images. NeuroImage, 17(2):825-841, 2002. "],
},
{
  "interface":"nipype.interfaces.fsl.preprocess.FAST",
  "name":"FSL FAST",
  "description":"FAST (FMRIBs Automated Segmentation Tool) segments a 3D image of the brain into different tissue types (Grey Matter, White Matter, CSF, etc.), whilst also correcting for spatial intensity variations (also known as bias field or RF inhomogeneities). The underlying method is based on a hidden Markov random field model and an associated Expectation-Maximization algorithm. The whole process is fully automated and can also produce a bias field-corrected input image and a probabilistic and/or partial volume tissue segmentation. It is robust and reliable, compared to most finite mixture model-based methods, which are sensitive to noise.",
  "citation":"Zhang, Y. and Brady, M. and Smith, S. Segmentation of brain MR images through a hidden Markov random field model and the expectation-maximization algorithm. IEEE Trans Med Imag, 20(1):45-57, 2001.",
},
{
  "interface":"nipype.interfaces.fsl.maths.Threshold",
  "name":"FSL Threshold",
  "description":"use following number to threshold current image (zero anything below the number)",
},
{
  "interface":"nipype.interfaces.io.DataSink",
  "name":"IO DataSink",
  "description":"DataSink: Generic named output from interfaces to data store",
},
{
  "interface":"nipype.interfaces.spm.preprocess.Smooth",
  "name":"SPM Smooth",
  "description":"Smooth (ie convolve) image volumes with a Gaussian kernel of a specified width. It is used as a preprocessing step to suppress noise and effects due to residual differences in functional and gyral anatomy during inter-subject averaging.",
  "citation":"SPM12 Manual",
},
{
  "interface":"nipype.algorithms.modelgen.SpecifySPMModel",
  "name":"Specify SPM Model",
  "description":"Specifiy SPM Model parameters",
},
{
  "interface":"nipype.interfaces.spm.model.EstimateContrast",
  "name":"SPM Estimate Contrast",
  "description":"Use spm_contrasts to estimate contrasts of interest",
},
{
  "interface":"nipype.interfaces.spm.model.Level1Design",
  "name":"SPM Level1Design",
  "description":"Generate an SPM design matrix",
},
{
  "interface":"nipype.interfaces.utility.wrappers.Function",
  "name":"User Defined Function",
  "description":"See parameters for function defition. User defined function.",
},]

interface_dict = {}
for interface in interfaces:
    interface['@type'] = 'SoftwareSourceCode'
    r = requests.post('http://mds/shoulder/ark:99999',data = json.dumps(interface))
    minted = r.json()['created']
    interface_dict[interface['interface']] = minted

interface_dict

r = requests.post('http://mds/shoulder/ark:99999',data = json.dumps(interface_dict))

interface_dict_id = 'ark:99999/218fcfb4-e2e3-4114-8562-e2ed765111b8'
