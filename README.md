# IMR - Intelligent Mobile Robot 

To Applied AI in mobile robotics

ได้เขียนโปรแกรม ในการควบคุมหุ่นยนต์ Mobile Robot ในด้าน AI and Machine Learning หลากหลายอย่าง เช่น Fuzzy, Genetics Algorithm, Artificial Life, Neural Networks, Reinforcement Learning, Naïve Bayes โดยจะมี Environment มาให้อยู่บนภาษา Python [PySimbot](https://github.com/jetstreamc/PySimbot)

<div align="center">
  <img height="300" src="https://user-images.githubusercontent.com/38836072/163747471-84b29dc6-0433-4213-945c-08ae7984754e.png">
  <img height="300" src="https://user-images.githubusercontent.com/38836072/163747476-f209bcf9-722e-4b01-9361-4439a289f5c8.png">
  
  Environment ของ PySimbot
</div>
  
<!--Reinforcement Learning robot-->
## Reinforcement Learning robot
[Video](https://www.youtube.com/watch?v=k3BVSOvV5u8)

โดยการที่ไม่มีค่า Epsilon-Greedy Decay ที่จะทำให้หุ่นยนต์นั้นมีตาราง Q-Table ที่จะใช้เวลาในการทำให้ค่าสมบูรณ์นั้นนานมาก ผมจึงลองทำ Epsilon-Greedy Decay Algorithm ขึ้นมาให้มัน Explore เยอะๆในช่วงแรกแล้วค่อย Exploitation เมื่อตาราง Q-Table เริ่มดีแล้ว โดยวิธีนี้ได้ผลดีมาก และ สามารถทำงานได้อย่างรวดเร็ว นอกจากนี้ผมได้ใช้ 5 Action โดยที่เพิ่มมาคือ Close ไกล้อาหารโดยให้พุ่งไปหาอาหาร แล้วอีก Action คือ Back ให้สามารถเดินถอยหลังเมื่อชนกำแพงได้ ผลที่ได้ค่อนข้างดีโดยสามารถหลบสิ่งกีดขวางได้เองตอนช่วงหลัง

<div align="center">
  <img height="300" src="https://user-images.githubusercontent.com/38836072/163748063-1e56ac99-946c-4cc2-99d8-864bbaad4ebd.png">
  
  กราฟแสดงการพัฒนาของหุ่นยนต์ 
</div>

<!--Naïve Bayes Robot-->
## Naïve Bayes Robot
[Video](https://youtu.be/FdqGhlOucJ0)

จากการ Training Dataset หลากหลายรูปแบบพบว่า NB รู้ทุกอย่างเป็น probability ทำให้ไม่สามารถ sensing location หรือระบุตำแหน่งได้ จึงเกิดปัญหาเวลาที่หุ่นยนต์เดินไปในสภาวะที่เป็นช่องแคบเหมือนกัน แต่มีความยาวไม่เท่ากัน ทำให้บางครั้งหุ่นยนต์ไม่สามารถออกจากสถานที่ดังกล่าวได้ หรือ ถ้าเอาหุ่นยนต์ไปใช้ในสถานที่จริงก็จะมีความผิดพลาดสูง low robustness แต่ก็มีข้อดีตรงที่สามารถทำงานได้รวดเร็วมากกว่า Algorithm แบบอื่นเหมาะกับหุ่นยนต์ที่ทำงานซ้ำๆ และใช้พลังงานในการคำนวณน้อย นอกจากนี้จำนวณข้อมูลที่ใช้ไม่ได้มีความสำคัญเท่ากับข้อมูลที่ ความแม่นยำในการหลบหลีก และ การเล็งมุมของอาหารให้ถูกต้อง

<!--Genetics Algorithm Robot-->
## Genetics Algorithm Robot
[Video](https://youtu.be/jNgFGnaLr1Y)

**Multi objective**
1. Lowest collision 
2. smooth movement and turning
3. No point-less spinning / turning
4. Walk Forward

**Mutation Method**
Dynamic mutation rate 1% at the beginning till 20 and increase to mild mutation function phase (21-30) and extreme mutation phase later 31-40 same method as the way I use to increase the number of mutation points.

**Robustness**
after state 50 try to change the position of the objective. I found out that this method works perfectly (and better than the original version), even the mean dropped in the extreme mutation phase, it still gave us new best which couldn't get from cross, but after change the objective's position and the global best changed to the lower fitness but become more robust and more reliable on every objective position. But when increase more objective, the initial random effect impact on colony converged fitness also become much higher. 


<div align="center">
  <img height="400" src="https://user-images.githubusercontent.com/38836072/163748365-a2690424-ff60-4823-b064-70c8ba3f004b.png">
  
  Learning Curve of GA Robot
</div>

<!--Artificial Life Robot-->
## Artificial Life Robot
[Video](https://youtu.be/9x1y5knal7A)

การค้นพบหลังจากการที่ลอง Simulation มาหลายครั้ง
1.	เราสามารถเปรียบเทียบ การเพิ่มลด energy ของแต่ละสถานการณ์ เป็นเหมือนกับตัวกำหนด gene เด่น
2.	ลักษณะเด่นที่จะ dominate ทั้ง colony จะขึ้นกับความซับซ้อน ของ environment พอเปลี่ยนไปใช้แมพเดิม มันเลือกที่จะไม่กิน แต่ไม่ชนมากกว่า เดินไปกินแล้วชนจนตายไปหมด ทำให้ทั้ง colony เดินวนๆไม่ยอมกิน อาจแก้ได้จากการเพิ่มจำนวนตัวเพื่อเพื่อความหลากหลาย
3.	ถ้าเราใช้ลักษณะเด่นของการวิ่งไปกิน dominate colony มากๆ มันจะไม่ converge การตายลงไปต่ำกว่า50/2000 ใน 1 แสน เพราะมันจะรีบไปกินกันอย่างเร็วมากๆ (เร็วกว่าทุกเคส converge ที่ส่งมา) มันจะหันไปกินอันใกล้ตลอด จะชนกันเอง ตัวหนึ่งก็จะรีบไปอาหาร อีกตัวก็รีบไป ไม่ยอมหลีกตายแล้วเกิดที่ใหม่มากินได้ไวกว่า
4.	จะดีกว่าถ้าสามารถแยกการชน กันเอง กับ ชนกำแพง เป็นคนละเคส เพราะมันจะไปติดกระจุกๆอยู่บริเวณขอบบนซ้าย และ ล่างซ้าย หรือจุดที่มีความคับแคบ
5.	เราจะทำให้มัน converge ได้ต่ำๆ ง่ายๆเลย ถ้ามันกินไม่ถี่ ทั้งนี้พฤติกรรมพวกนี้ขึ้นกับการตั้ง สถานการณ์ ปริมาร +/- ที่ต้องตอนต้น โดยยิ่งใช้ Sample Space มากก็จะทำให้ Converged เร็วมากขึ้นเท่านั้น
6.	ถ้าตั้งการ +/- ด้วยตรรกยะที่ซับซ้อนไป มันจะกลายเป็น ข้อจำกัดให้ colony ไม่ดีและ converge ยากในภายหลัง

<div align="center">
  <img height="400" src="https://user-images.githubusercontent.com/38836072/163748511-03e72749-b38e-4df4-a0e2-4dbdd27708e0.png">
  
  กราฟการตายของ ALIFE Robot ที่ตายน้อยลง เพราะมีการเรียนรู้
</div>


<!-- Contact-->
## Contact
Saksorn Ruangtanusak - [Linkedin](https://www.linkedin.com/in/saksorn/)

Project Link: [https://github.com/huak95/IMR](https://github.com/huak95/IMR)
