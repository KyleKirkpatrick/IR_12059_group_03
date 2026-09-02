PROGRAM main
  VAR
    button_conveyor : BOOL;
    motor_conveyor : BOOL;
    pulse_package : BOOL;
    button_reset : BOOL;
    number_package : INT;
    counter_package : CTU;
  END_VAR

  motor_conveyor := button_conveyor;
  counter_package(CU := pulse_package, R := button_reset, PV := 100);
  number_package := counter_package.CV;
END_PROGRAM

PROGRAM wb_counter
  VAR
    CTD0 : CTD;
    CTU0 : CTU;
    CTU1 : CTU;
    CTU2 : CTU;
    CTU3 : CTU;
    CTU4 : CTU;
    CTU5 : CTU;
    CTU6 : CTU;
  END_VAR
  VAR
    Weight_sensor AT %MW0 : INT;
    Button AT %QX0.0 : BOOL;
    Motor AT %QX0.1 : BOOL;
    Pulse AT %QX0.2 : BOOL;
    Reset AT %QX0.3 : BOOL;
    Total_Count AT %MW1 : INT;
    Bigboxcount AT %MW2 : INT;
    MediumboxCount AT %MW3 : INT;
    SmallboxCount AT %MW4 : INT;
    IsBig AT %MX0.0 : BOOL;
    IsMed AT %MX0.1 : BOOL;
    IsSml AT %MX0.2 : BOOL;
  END_VAR
  VAR
    R_TRIG1 : R_TRIG;
    R_TRIG2 : R_TRIG;
    R_TRIG3 : R_TRIG;
    _TMP_GT3264721_ENO : BOOL;
    _TMP_GT3264721_OUT : BOOL;
    _TMP_GT5192271_ENO : BOOL;
    _TMP_GT5192271_OUT : BOOL;
    _TMP_GT8242294_ENO : BOOL;
    _TMP_GT8242294_OUT : BOOL;
    _TMP_ADD7064305_ENO : BOOL;
    _TMP_ADD7064305_OUT : INT;
  END_VAR

  Motor := Button;
  _TMP_GT3264721_OUT := GT(EN := TRUE, IN1 := Weight_sensor, IN2 := 10, ENO => _TMP_GT3264721_ENO);
  IF _TMP_GT3264721_ENO THEN
      IsBig := _TMP_GT3264721_OUT;
  END_IF;
  _TMP_GT5192271_OUT := GT(EN := NOT(IsBig), IN1 := Weight_sensor, IN2 := 5, ENO => _TMP_GT5192271_ENO);
  IF _TMP_GT5192271_ENO THEN
      IsMed := _TMP_GT5192271_OUT;
  END_IF;
  _TMP_GT8242294_OUT := GT(EN := NOT(IsMed) AND NOT(IsBig), IN1 := Weight_sensor, IN2 := 0, ENO => _TMP_GT8242294_ENO);
  IF _TMP_GT8242294_ENO THEN
      IsSml := _TMP_GT8242294_OUT;
  END_IF;
  R_TRIG1(CLK := Pulse);
  CTU3(CU := IsBig AND R_TRIG1.Q, R := Reset, PV := 100);
  Bigboxcount := CTU3.CV;
  R_TRIG2(CLK := Pulse);
  CTU5(CU := IsMed AND R_TRIG2.Q, R := Reset, PV := 100);
  MediumboxCount := CTU5.CV;
  R_TRIG3(CLK := Pulse);
  CTU6(CU := IsSml AND R_TRIG3.Q, R := Reset, PV := 100);
  SmallboxCount := CTU6.CV;
  _TMP_ADD7064305_OUT := ADD(EN := TRUE, IN1 := Bigboxcount, IN2 := MediumboxCount, IN3 := SmallboxCount, ENO => _TMP_ADD7064305_ENO);
  IF _TMP_ADD7064305_ENO THEN
      Total_Count := _TMP_ADD7064305_OUT;
  END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 1);
    PROGRAM instance0 WITH task0 : wb_counter;
  END_RESOURCE
END_CONFIGURATION
