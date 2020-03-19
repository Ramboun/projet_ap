#!/usr/bin/env bash

scriptsinstances=/home/vavalm/PycharmProjects/projet_ap/JSPLIB/instances/
scriptspython=/home/vavalm/PycharmProjects/projet_ap/src/
resultat=/home/vavalm/PycharmProjects/projet_ap/results/GA/

cd $scriptsinstances
for instance in la3*;
do
  echo  $instance;
  cd /home/vavalm/PycharmProjects/projet_ap/src
  python $scriptspython/GA.py --instance_name $instance > $resultat/$instance.txt;
  echo  "$instance done";
done

echo  "That's finished";