function spectrumZoom(aJSONString)
{
	var info = JSON.parse(aJSONString)
	var actDoc = mainWindow.activeDocument
	var spc = new NMRSpectrum(actDoc.getItem(info.itemId));
	if (!spc.isValid())
		return false;
	spc.horzZoom(-0.5, 10.5);
	spc.vertZoom(-0.1, 0.8);
	/*if( spc.dimCount == 1)
		spc.zoom(3.0, 4.5);
	else
		spc.zoom(1.0, 5.0, 1.0, 5.0);*/
	//spc.zoom();
	spc.update();
	mainWindow.activeWindow().update();
	return true
}
Application.mainWindow.installEventHandler("nmrSpectrumImported", "spectrumZoom")