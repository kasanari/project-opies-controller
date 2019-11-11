var angle_slider = document.getElementById("wheel_angle");
var drive_slider = document.getElementById("drive_speed");

var angle_slider_out = document.getElementById("wheel_angle_indicator");
var drive_slider_out = document.getElementById("drive_speed_indicator");

angle_slider_out.innerHTML = angle_slider.value; // Display the default slider value
drive_slider_out.innerHTML = drive_slider.value; // Display the default slider value

angle_slider.oninput = function() {
  angle_slider_out.innerHTML = this.value;
  sendCarControl()
};

drive_slider.oninput = function () {
  drive_slider_out.innerHTML = this.value;
  sendCarControl()
};

function resetSliders() {
  angle_slider.value = 0.5;
  drive_slider.value = 0.5;
  angle_slider_out.innerHTML = angle_slider.value; // Display the default slider value
  drive_slider_out.innerHTML = drive_slider.value; // Display the default slider value
}