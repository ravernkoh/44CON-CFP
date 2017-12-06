// clipboardjs.com
// Store text from targeted element to clipboard

var clipboard = new Clipboard('.copy-text');
clipboard.on('success', function(e) {
    console.log(e);
});
clipboard.on('error', function(e) {
    console.log(e);
});
