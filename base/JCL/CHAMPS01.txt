//CHAMPS01 JOB 1,NOTIFY=Z26069,MSGCLASS=X,MSGLEVEL=(1,1)
//JOBLIB   DD  DSN=Z26069.LOAD,DISP=SHR
//**********************************************************************
//REINIT  EXEC PGM=IDCAMS
//SYSPRINT  DD SYSOUT=X
//SYSIN     DD *
  DELETE Z26069.TOPLANE         NVSAM
  DELETE Z26069.MIDLANE         NVSAM
  DELETE Z26069.BOTLANE         NVSAM
  DELETE Z26069.JUNGLE          NVSAM
  DELETE Z26069.TOPLANE.REPORT  NVSAM
  DELETE Z26069.JUNGLE.REPORT   NVSAM
  DELETE Z26069.MIDLANE.REPORT  NVSAM
  DELETE Z26069.BOTLANE.REPORT  NVSAM

  IF LASTCC=08 THEN
     SET MAXCC=00
  END
/*
//**********************************************************************
//*                SEPARATE CHAMPIONS BY ROLE                          *
//**********************************************************************
//STEP01  EXEC PGM=CMPINIT
//STEPLIB   DD DSN=Z26069.LOAD,DISP=SHR
//INFL      DD DSN=Z26069.CHAMPION.DATA,DISP=SHR
//OUTFL1    DD DSN=Z26069.TOPLANE,
//             DISP=(NEW,CATLG,DELETE),
//             SPACE=(TRK,(1,1),RLSE),
//             RECFM=FB,
//             LRECL=100,
//             DCB=DSORG=PS
//OUTFL2    DD DSN=Z26069.MIDLANE,
//             DISP=(NEW,CATLG,DELETE),
//             SPACE=(TRK,(1,1),RLSE),
//             RECFM=FB,
//             LRECL=100,
//             DCB=DSORG=PS
//OUTFL3    DD DSN=Z26069.BOTLANE,
//             DISP=(NEW,CATLG,DELETE),
//             SPACE=(TRK,(1,1),RLSE),
//             RECFM=FB,
//             LRECL=100,
//             DCB=DSORG=PS
//OUTFL4    DD DSN=Z26069.JUNGLE,
//             DISP=(NEW,CATLG,DELETE),
//             SPACE=(TRK,(1,1),RLSE),
//             RECFM=FB,
//             LRECL=100,
//             DCB=DSORG=PS
//PRTLINE   DD SYSOUT=X
//SYSOUT    DD SYSOUT=X
//SYSPRINT  DD SYSOUT=X
//CEEDUMP   DD DUMMY
//SYSDUMP   DD DUMMY
//*
//UNOSC PROC RLE=
//STEP1   EXEC PGM=CMPROC
//INFL1      DD DSN=Z26069.&RLE,DISP=SHR
//OUTFL1     DD DSN=Z26069.CHAMPS.VSAM,DISP=SHR
//OUTFL2     DD DSN=Z26069.&RLE..REPORT,
//             DISP=(NEW,CATLG,DELETE),
//             SPACE=(TRK,(1,1),RLSE),
//             RECFM=FB,
//             LRECL=100,
//             DCB=DSORG=PS
//PRTLINE   DD SYSOUT=X
//SYSOUT    DD SYSOUT=X
//SYSPRINT  DD SYSOUT=X
//CEEDUMP   DD DUMMY
//SYSDUMP   DD DUMMY
// PEND
//**********************************************************************
//STEP02  EXEC UNOSC,RLE=MIDLANE
//STEP03  EXEC UNOSC,RLE=JUNGLE
//STEP04  EXEC UNOSC,RLE=TOPLANE
//STEP05  EXEC UNOSC,RLE=BOTLANE