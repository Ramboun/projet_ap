#!/usr/bin/env bash

scriptsinstances=/home/vavalm/PycharmProjects/projet_ap/JSPLIB/instances/
scriptspython=/home/vavalm/PycharmProjects/projet_ap/src/
resultat=/home/vavalm/PycharmProjects/projet_ap/results/GA/
#resultat=/home/vavalm/PycharmProjects/projet_ap/results/PLNE/

cd $scriptsinstances
for instance in la*;
do
  echo  $instance;
  cd /home/vavalm/PycharmProjects/projet_ap/src
  python $scriptspython/GA.py --instance_name $instance > $resultat/$instance.txt;
#  python $scriptspython/exact_method.py --instance_name $instance --display 0 > $resultat/$instance.txt;
  echo  "$instance done";
done

echo  "That's finished";