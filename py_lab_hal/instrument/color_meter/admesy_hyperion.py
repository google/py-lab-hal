# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Child Colormeter Module of Admesy Hyperion."""

from py_lab_hal.instrument.color_meter import color_meter


class AdmesyHyperion(color_meter.ColorMeter):
  """Child Colormeter Class of Admesy Hyperion."""

  def measure_XYZ(self) -> str:
    """Measure XYZ.

    Returns:
        str: X, Y, Z, clip, noise
    """
    return self.data_handler.query(':MEASure:XYZ')

  def measure_Yxy(self) -> str:
    """Measure Yxy.

    Returns:
        str: Y, CIEx, CIEy, clip, noise
    """
    return self.data_handler.query(':MEASure:YXY')

  def measure_Yuv(self) -> str:
    """Measure Yuv.

    Returns:
        str: Y, u, v, clip, noise
    """
    return self.data_handler.query(':MEASure:YUV ')

  def measure_CCT(self) -> str:
    """Measure CCT.

    Returns:
        str: CCT, clip, noise
    """
    return self.data_handler.query(':MEASure:CCT')

  def measure_luminance(self) -> str:
    """Measure luminance.

    Returns:
        str: Y, clip, noise
    """
    return self.data_handler.query(':MEASure:Y')

  def measure_colortemp(self) -> str:
    """Measure temperature.

    Returns:
        str: temperature
    """
    return self.data_handler.query(':MEASure:TEMPerature ')

  def measure_flicker(self, method: int, samples: int, delay: int) -> str:
    """Measures MIN/MAX, RMS, JEITA, VESA, percentage or index flicker.

    Args:
        method: Flicker method. 0=MIN/MAX, 1=RMS, 2=JEITA, 3=VESA, 4=percentage,
          5=index.
        samples: Number of samples.
        delay: delay.

    Returns:
        str: MIN/MAX, RMS, JEITA, VESA, percentage, or index value.
    """
    return self.data_handler.query(
        f':MEASure:FLICKer {method},{samples},{delay}'
    )

  def measure_dwl(self) -> str:
    """measure dominant wavelength.

    Returns:
        str: DWL, Pe, Y, CIEx, CIEy, clip, noise.
    """
    return self.data_handler.query(':MEASure:DWL')

  def measure_dark(
      self, x_limit: float, y_limit, z_limit: float, average: float
  ) -> str:
    """Measures dark and check against the limits.

    Args:
        x_limit: X limit.
        y_limit: Y limit.
        z_limit: Z limit.
        average: average.

    Returns:
        str: temperature, darkOK, X, Y, Z, X, Y, Z, etc.
    """
    return self.data_handler.query(
        f':MEASure:DARK {x_limit},{y_limit},{z_limit},{average}'
    )

  def measure_fast_dark(
      self, x_limit: float, y_limit, z_limit: float, average: float
  ) -> str:
    """Measures dark and check against the limits in fast mode.

    Args:
        x_limit: X limit.
        y_limit: Y limit.
        z_limit: Z limit.
        average: average.

    Returns:
        str: temperature, darkOK, X, Y, Z, X, Y, Z, etc.
    """
    return self.data_handler.query(
        f':MEASure::FASTDARK {x_limit},{y_limit},{z_limit},{average}'
    )

  def measure_frequency(self, samples: int) -> str:
    """Measure the detected frequency of the DUT plus the amplitude of this frequency.

    Args:
        samples: Number of samples.

    Returns:
        str: frequency, amplitude, clip
    """
    return self.data_handler.query(f':MEASure:FREQuency {samples}')

  def measure_sequence_Y(self, frames: int) -> str:
    """Measures Y of a specified number of frames.

    Args:
        frames: Number of frames.

    Returns:
        str: Y, clip, noise.
    """
    return self.data_handler.query(f':MEASure:SEQY {frames}')

  def measure_sequence_XYZ(self, frames: int) -> str:
    """measures XYZ of a specified number of frames.

    Args:
        frames: Number of frames.

    Returns:
        str: X, Y, Z, clip, noise
    """
    return self.data_handler.query(f':MEASure:SEQXYZ {frames}')

  def measure_delta_temp(self) -> str:
    """Delta of current temperature versus the temperature at which dark calibration was done.

    Returns:
        str: delta temperature
    """
    return self.data_handler.query(':MEASure:DTCAL')

  def measure_sample_Y(self, samples: int, delay: int) -> str:
    """Measures in sample mode using a fixed integration time of 500us.

    When auto-range is enabled, this will adjust the gain.

    Args:
        samples: Number of samples.
        delay: Delay in number of samples.

    Returns:
        str: dt, clip, Y data
    """
    return self.data_handler.query(f':SAMPLE:Y {samples},{delay}')

  def measure_sample_XYZ(self, samples: int, delay: int) -> str:
    """Measures in sample mode using either autorange or a fixed integration time.

    Parameters have the same meaning as with “:SAMPle:Y”. The returned data is
    in XYZ format.

    Args:
      samples: Number of samples.
      delay: Delay in number of samples.

    Returns:
      str: dt, clip, XYZ data.
    """
    return self.data_handler.query(':SAMPle:XYZ {samples},{delay}')

  def measure_all(self) -> str:
    """Measure all data XYZ and Yxy calibrated, XYZ without Calibration and XYZ saturation.

    Returns:
        str: X,Y,Z,Y,x,y,Xoff,Yoff,Zoff, Xsat,Ysat,Zsat,clip,noise.
    """
    return self.data_handler.query(':MEASure:ALL ')
