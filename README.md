# TSDetective

## Method

The idea behind this method is to gather some 'evidence' if a given time series was used to train some foundation model.

To test this - we will take the original series and apply some transformation to it. Hopefully, the transformation is one that will confuse a pre-trained model but maintain the key singals of the series.

Then we simple fit an AutoARIMA to both the original and synthetic series and predict on a test set. We will use the ratio of the errors as our measure to compare vs a foundation model's error on both the original and synthetic series.

If the ratio of errors (Arima Ratio / Foundation Ratio) is greater than 1 then the foundation model had trouble fitting the new series more than the ARIMA - the higher the number then that is more 'evidence'. On the contrary, around and less than 1 implies that it's a toss up if the foundation model had seen the series.

The hope is that the AutoARIMA ratio is very close to 1 (implying the synthetic series is similar enough to the original), this way any deviation from the foundation model's accuracy would be very interesting to note!

## Caveat

I do not think this method is anywhere near 'perfect', and view it more of a simple proof of concept. You should not make claims based on the outputs of the method, but hopefully it gets you thinking about some ways to engage with large time series methods beyond just asking for a forecast!

