# Recording.mp4 — presentation transcript

Source: Recording.mp4. Duration: 29 minutes 18 seconds. Presentation date: 5 November 2026. Transcribed locally on 10 November 2026.

Machine-generated transcript, checked against a second speech-model pass and the supplied slides for names and technical terminology. This is a lightly edited record, not a certified verbatim transcript. Speakers have not been reliably diarised. Timestamps are approximate. Setup audio and several live-demo exchanges are indistinct and are marked in brackets; unresolved words have not been guessed. Spoken claims are preserved and are assessed separately in the report. The recording ends as Q&A begins.

## Chapters

- **00:00** — Setup audio and indistinct speech
- **01:20** — Hotel context and project introduction
- **04:01** — Service quality and LQA
- **06:00** — Satisfaction and personalisation
- **09:40** — Current practice and information handover
- **12:52** — First-time guests and design challenge
- **13:58** — Functions, requirements, and concepts
- **17:02** — Proposed journey and visualisation
- **18:10** — Technical implementation and iterations
- **20:03** — Preference-extraction experiments
- **20:51** — Display design and contextual retrieval
- **23:18** — Usability findings and requirements check
- **24:54** — Limitations and next steps
- **25:59** — Live demonstration
- **28:52** — Opening Q&A; file ends

## Transcript

### 00:00–01:20

[Setup audio, silence and indistinct speech; no reliable word-for-word transcription.]

### 01:20–01:46

Let's pretend you're choosing a lovely hotel to stay at in Singapore.

### 01:46–02:14

There are a lot of options, and honestly there's really no right choice. Guests choose the hotel they want to stay at based off of multiple different factors, like the star rating, its reviews, and even how much they charge per night. Currently, Singapore has 408 licensed hotels, which means you have plenty of options to choose from. But zooming into the luxury hospitality segment, almost 50% of the market is dominated by just five players.

### 02:15–02:31

In an industry that's so cutthroat and competitive, what makes these five players so special that they occupy such a big part of the pie? Good afternoon, I'm Neha, and our team is exploring how we can drive profit margins for hotels, especially in the luxury industry [final phrase unclear].

### 02:33–02:59

Now, profit for hotels looks very similar to any other industry. It's really just revenue minus cost. But our industry partner said they're noticing diminishing profits recently, mostly due to increasing manpower and operational costs. Now, if we try to reduce costs of luxury hotels, it might be counterintuitive because guests expect a certain standard of products and services. So let's focus on how we can increase revenue instead.

### 03:02–03:27

Now, revenue in hotels is measured by this term called RevPAR, or revenue for available room, which is essentially the product of the average daily rate of the hotel and the occupancy rate. Now, there are some factors that both of these terms have in common. They're both influenced by the location of the hotel, the season that you book it in, economic conditions, and the competitive landscape. However, all of these are factors

### 03:27–03:53

that are not really in the hotel's control. So what can be controlled? Average daily rate heavily depends on classification, or the star rating of a hotel, which is why five-star hotels can afford to charge so much more than a three-star or four-star hotel and still be justified in their prices. On the other hand, occupancy rate heavily depends on reputation and reviews, which is a direct representation of customer satisfaction.

### 03:56–04:23

So let's look at how we're going to try to include both of these factors, starting with classification. In luxury hotels, classification is a measure of the hotel's quality. which is measured by Leading Quality Assurance, an industry-wide standard. Now, LQA consists of various different standards across different departments and dimensions. It measures things like your emotional intelligence, the personalization in your service, sustainability, and so much more.

### 04:23–04:50

And it's not just a one-time thing. Hotels consistently get audited to make sure that they meet these standards. So in order for our hotels to increase their ranking and their ratings, they need to be compliant with as many of these standards as possible. And if you notice, these are just a few of the many, many standards, and they're very, very specific. But we noticed a trend among a lot of these standards. A lot of them revolve around how personalized your service is for guests.

### 04:53–05:18

Now, we talked to our industry partner, and they said they noticed a gap in following these standards. Staff follow them when there's someone paying attention to them. But when they're not, it's very difficult for staff to keep track. Now, this could be due to multiple different factors. It could be staff negligence, or it could even be just overworked staff. When you have so many different standards to follow, how do you still make sure you follow all these standards while still delivering service? [Short phrase unclear.]

### 05:20–05:47

So to mitigate this, our industry partner have tried multiple times. They even hired the first female butler that ever served the queen to come down and train their staff. Along with this, they also do very frequent training programs for all their staff. And yet, the gap still persists. Our industry partner quoted one specific incident that stood out, where there was a sick person in the lobby, and there were staff around, but none of them noticed because they were all mixed up in a lot of different tasks [last phrase unclear].

### 05:48–05:57

In this sort of situation, there's really missing interpersonal communication and a gap in making sure you cater service towards individual guests.

### 06:00–06:25

On the other hand, reputation and reviews heavily depend on customer satisfaction. Now, occupancy rate comes from two different paths. If you have a satisfied guest, then you tend to be loyal members coming back, including your occupancy rate. On the other hand, satisfied guests also post good reviews about your hotel, driving and customer acquisition. So it's a multi-factor increase in occupancy.

### 06:25–06:49

Now, we conducted surveys on guests, and we asked them what hotels made them want to return. And they said, one of them said, quoted Marriott's loyalty program in particular, saying that their consistent standards really helped them want to keep coming back to the hotel. Now we did some market research and this shows you the number of members of Marriott that were

### 06:49–07:16

returning guests. So out of all of Marriott's guests, two-thirds of them happened to be returning members, which just shows you how important customer satisfaction is to hotel. But there's a bit of a gap in satisfaction right now in that it's been fairly stagnant over the past few years. It did rise a little bit from the COVID years, but all in all, it seems to be capped at a pretty constant threshold. Now, why is this happening?

### 07:16–07:44

One major reason is rising expectations. When luxury service becomes the standard, people start expecting more time. Now, the problem here is that they start expecting different things as well. For example, a lot of hotels around Singapore and [unclear] have implemented automated check-in kiosks. We've seen this at PARKROYAL. We've even seen this at [hotel name unclear] at NUS. And this has kind of mixed reviews. There's one demographic of people that really enjoy this kind of service.

### 07:44–08:11

They can just check in and move on with it. There's another demographic that isn't a big fan because they expect to be treated face-to-face and have a personalized experience when they enter the hotel. So when we increase the number of automations and try to scale these kind of features in hotels, often it ends up in standardization. So how do we meet different expectations of different guests? we need to make sure that we can cater experiences to be more individualized.

### 08:11–08:33

So let's recap. We've now understood that revenue for available room depends on ADR and occupancy. Both of these factors are heavily influenced by the quality of service hotel provide, as well as customer satisfaction. We know that there's a big gap in terms of how personalized this service is

### 08:33–08:59

and how customer satisfaction is very related to how individualized your service is. Which is why we as a group are exploring how we can improve personalisation in luxury hotels. So now, enough with the theories of why do we actually need personalization, we want to know if actually the customers and businesses really want it. So from our secondary research, we know that 86% of the travelers

### 08:59–09:27

actually sought to have at least one of their experiences to be personalized. And also, 61% of consumers are actually willing to pay more if their experiences are personalized, which means that it can actually help to drive out ADR, which actually links up to RevPAR, which helps with the business for the hotel. 87% of the guests are also more likely to recommend a hotel, which links to our acquisition path, where more customers might be coming as new guests when there are better reviews.

### 09:27–09:38

Our business partner also said that they actually see the impact when they try to do personalization in their operations right now, which helps to support this need for personalization to increase retention.

### 09:40–10:07

We've actually been to a few case studies. This includes places like the Accor Group, where they are in charge of Sofitel and Novotel, as well as [hotel name unclear] at NUS, and also our business partners, which is PARKROYAL [location unclear]. So maybe I'll just go through one of the case studies, which is under the Accor Group, to give you a better understanding of what most of these hotels are doing for personalization. Well, most of them have this database where they store this personalized info.

### 10:07–10:32

So the general manager will usually retrieve them and during the morning brief, brief the staff on the floor on the customer profiles and things to look out for to personalize their experiences. Then, hard copy notes or information might be thumbed down on WhatsApp such that when the staff forgets any of this information, they can actually refer back to them as fallback. Then the service will be personalized to the guests when they come. And this information comes from the morning brief and the profiles.

### 10:32–10:58

Afterwards, new information that are being acquired during the conversation with the guests are then being pumped back into the database to give the profiles a richer context. So let's break down what actually falls short for personalization. Well, for the database and the hard copy notes for fallback, there's actually only a single source or retrieval for the data. And a lot of this information is forgotten during the service period, which causes them to

### 10:58–11:26

need to frequently look up the hard copy. And they also find it very hard to find the information on these guests and sometimes they are even unable to identify the guests that they need to personalise because they have to try to identify the guests from simply written with descriptions or the profile pictures in the database. Then, during the service, it is also hard for them to refer to these personalised notes during the conversation as they have to uphold a certain professionalism for their service,

### 11:26–11:53

which means they have to do personalisation from their memory. And it's hard for the staff to maintain a natural flow of the conversation while doing this, as well as being tasked to do additional questions on the customers, such that they can gain new info to update their database on data. Lastly, for the entry, every staff actually has their own interpretation, their own way of understanding the customer's needs, which means they actually have an inconsistent way of entering new knowledge into the database.

### 11:53–12:17

As well as the staff are actually busy with a lot of workload, which means that they can only enter the data when they are free. And this means that they might take a while before the staff enters the new data, and they might actually forget some of this data, as well as some of this data might be corrupted in their memory. So the lack of the seamless recognition of the guests and the ease of finding and filtering

### 12:17–12:45

information cause us to need recognition, as well as fast retrieval of information. Secondly, the lack of information retrieval during the conversation itself, and the difficulty in asking new questions to gather data, cause us to need the ease of referencing information while maintaining professionalism. Lastly, the lack of effortless data entry with consistent formats and accurate data inputs in your system cause us to need easy data inputs and reliable processing processes

### 12:45–13:12

such as the data are standardized and useful. So we have already told you the issues with personalization as a whole, but this issue is even more prevalent for new guests because personalization is only being able to be done when there's information. So with no information, it's hard to personalize for them which leads to low satisfaction and the customers don't come back causing a large proportion of the customers

### 13:12–13:39

to be new customers. And this points to the two factors of being able to quickly enter information in database and real-time and fast retrieval of information to be even more crucial as these can help the data to be retrieved during the first day itself for the new guests and being able to try their best to personalize the experiences for them. This is also backed by our industry partner where they said that for the first-time guests, there's actually only a single-digit retention

### 13:39–13:54

rate for them. So with all these, we come to our design statement which is how might we actually enable luxury hotel staff to capture, share, and access relevant guest information seamlessly so that they can deliver consistent, personalised, high-quality service.

### 13:58–14:21

As mentioned before, we are going to capture information, enter information, retrieve information, and display the information. We have categorised these needs into two main functions, capture plus process, and display. For capture and process, you will be able to capture preferences and complaints of the guest, associate the interaction with the guest, and also process and store information for easy lookup.

### 14:21–14:48

For display, you will be able to select information for the current service task based on context and also display concise visuals so that the staff will be able to see important information quickly. So as mentioned before, we want to capture, display, and also retrieve without much disruption

### 14:48–15:15

of the natural conversation between the staff and the customer. So through this, from the two functions, we have [unclear] into two more criteria. So on-time service support and glanceable interaction allow staff to retrieve data quickly and also see data quickly so as to not disrupt the conversation and have a good service. Low effort capture addresses the need of capturing information and entering information easily

### 15:15–15:39

and it's not as difficult as before. And preference continuity allows staff to pass information from staff to staff so that there are more consistent loads and better standardized input. We also link these criteria into some of the LQA service standards, such as timely support, natural conversation, active listening, and personalized service.

### 15:39–16:02

How are we going to measure this is to have time taken for each of the criteria, such as below one second for the first visible cue, how long the staff needs to see the information, how many times the attention shifts, time capturing information, and whether the correct preference reaches the next staff.

### 16:02–16:29

We also compare the different ways to achieve these criteria, such as the current workflow, smart glasses, or even audio badge and earpiece. As you can see, for the current workflow, it is very manual as staff need to remember the customer, and also type all the information manually into the database. In comparison, if you use an audio badge and earpiece, the information of the guest can

### 16:29–16:55

be recorded automatically, but the staff still need to recognize the guest to be able to link the information and the guest's information. In the best case, which is your smart glasses, you can use computer vision to identify the guest, use the glasses display to have a concise cue [last word unclear], so that the staff will be able to see the guest information easily, hands-free audio capture and also record

### 16:55–17:19

information with a standardised format easily. So this will be our proposed current staff journey. When I see the customer, for example if I'm the staff, I will start capturing [unclear]. The glasses will retrieve the profile and show any relevant customer information such as allergy and Preference. If guests have a Preference and Allergy, the standardized approach is

### 17:19–17:37

to greet the guests, offer preference to guests, and also offer alternatives for food allergies. Else, they can do otherwise. And on this conversation, it's recorded, processed, and locked for further training. And also, it will be LQA-benchmarked. Next, we also have a short video demonstration

### 17:37–18:03

of how the proposed solution would work. As you can see, the staff will be able to see the guest information, name, preferences, allergies, also offer accordingly.

### 18:03–18:27

And all this information is tracked. Next, I will pass to Ping Hui, who will talk about [unclear]. Okay, so having seen how guests and staff interact with the smart glasses, now I will be talking about how we are going to implement it. So for the Capture Pipeline, we will have the smart glasses capture and record interaction with guests. Then this information will be processed to extract relevant insights

### 18:27–18:49

and it will be associated with guests through facial recognition and this data will be recorded in the database. So our first iteration involves changing the processing from continuous to temple-touch activation. This is to reduce the battery usage. Because our initial design has the smart glasses continuously process and record all frames,

### 18:49–19:17

even when the staff are not interacting with any guests, this wasted a lot of power. So now the staff will activate the session by pressing the temple, and it will only stop after 15 seconds of audio silence. This allows for pauses during conversations, and it prevents the recording to be continuous.

### 19:17–19:40

And this will cause a reduction in battery drainage by around 67%. Then our next iteration involves changing the processing from local to server. During our initial testing, we have all the heavy processing done within the glasses itself. And this causes the processing time to be around 1.6 seconds.

### 19:40–20:08

Thus, we look into the pipeline and we discover that there are a few steps that have processing that is very heavy. So we move all of those steps into the server so that it can be processed faster. This causes a reduction of the processing time to around 1.1 in a second, which corresponds to around a 30% reduction in processing time. So for preference extraction, we have two approaches that we are diving deep into.

### 20:08–20:34

So for the first approach, we have audio transcribed by Whisper, and we use the transcription to do a transcription that will be sent to a model for analysis. So we tested three models, and we found out that Qwen is the best model to extract preferences in the least amount of time. However, we found out that it might think questions or complaints

### 20:34–20:51

as preferences, which is inaccurate. That is why we need further iterations in our next step, before incorporating video input, which is for approach to see whether the higher processing power is being justified by the video input.

### 20:51–21:17

Then for the display of information, we are looking into the position of where the display information should be at. Then during our user testing, we found out that having the display information right inside the guest space is the best because this will reduce the time that the staff will

### 21:17–21:44

look away from the guest and is more easily interpreted. To do so, we will have face detection within the glasses itself, which will figure out the coordinates of the face to display the information right beside the guest. However, if we have too much information about the guest, the long description may get too long and the staff have to read all these long descriptions while maintaining a conversation

### 21:44–22:09

with the guest, which might be very disruptive. That is why we change these long descriptions into icons, so we split these main symbols into categories like food and room type. Then it will be labelled by markers. So a heart shape indicates a preference, and a warning sign indicates an allergy. This is so that the staff can easily interpret this design.

### 22:09–22:32

Then for our proposed iteration, we found out that for returning customers, they might have a long list of preferences. So displaying them all at once will still be very disruptive. Hence, we propose contextual retrieval of preferences. So what the solution will do is that you will take in the audio transcription of the interaction

### 22:32–23:00

and figure out the context of the interaction between guests. So for example, in a restaurant setting, when guests and staff are talking about food, they will show preferences only on food. And [unclear] the preferences on room type, which will disrupt the staff in the conversations. [Negation unclear in the audio.] So this is a simplified system architecture of our whole solution.

### 23:00–23:24

The key points are the glasses and the server will be communicating through Wi-Fi, and the guest database will be stored in the server, so it can be actively updated by all staff. And at the same time, they can be retrieved by all staff, so that there is a preference continuity as stated in our design requirement. So we conducted concept walkthrough and product testing with 10 participants.

### 23:24–23:51

However, they are not actual hotel staff, so it's mainly for usability testing. All of them mentioned that capturing information is easy. However, most participants found that to incorporate these visual cues into the interaction might be a bit challenging. So we have to conduct actual hotel testing to see whether is it cause of a lack of staff training

### 23:51–24:18

or is there any other ways we can improve our process. So we weigh our smart glasses against the design requirement that [name unclear] had stated earlier. So for on-time service support, we have to achieve our less than one second service window. However, we only managed to reduce it to 1.18 seconds. However, we believe that this could be improved further, because now currently all the processing is being done on my laptop,

### 24:18–24:41

which has limited processing power. Then for low-effort capture, I believe we can all agree that by simply tapping the temple of the glasses is very easy. Then for glanceable interaction, it is incomplete because it's still hard for staff to incorporate these visual cues into conversations, leading to occasional pauses and attention shifts.

### 24:41–25:04

And for our preference continuity, the shared database really allows all staff to receive the most updated information. However, preferences are still not being extracted consistently. So we will look into it in the next semester. The main limitation of our smart glasses is the PDPA concerns. Because it requires data consent for collecting and retaining these preferences data.

### 25:04–25:29

However, from our survey, most responders are willing to provide this data to have a more personalized service. This is our next step that we should be doing for our next semester. Key points such as preference extraction and contextual retrieval of preferences that I mentioned earlier.

### 25:29–25:55

Then we will also conduct actual hotel staff usability pilot testing to identify is there a need for staff training to incorporate these visual cues into conversations naturally. We might also have cues for staff to ask guiding questions to capture more preferences data. Then lastly, we will implement LQA scoring for each staff to ensure that they adhere

### 25:55–26:20

to service standards during their interaction with guests. So now we'll move on to the demo. [Brief demo setup speech unclear.]

### 26:20–26:46

We'll make sure it's connected. Move this up, right? It's connected already ah? It should be connected already ah.

### 26:46–27:11

Move it up. Move it up. [Brief demo setup speech unclear.] So the glasses output is shared on the screen

### 27:11–27:39

and you're using an Android emulator to show it. So when Ping Hui looks at me in the eye, he will capture my face and then show a preference

### 27:39–28:02

beside my face. And this is limited within the [field of view; wording unclear]. Yeah, you can try it and take a look. [Partly unclear.] [Demo discussion about position or focal distance; words unclear.] That's it. Okay. [Brief demo discussion unclear.] [Brief demo discussion unclear.] Nice. I think you touched the side.

### 28:02–28:29

[First phrase unclear.] You need to look already. You can see the name and the icon, looking around. You must look up. You must maintain eye contact. So if two persons are standing together, only when you are looking at [name unclear]. Sorry, sorry, sorry.

### 28:29–28:55

That's why I'm concerned that you have to keep looking at her. Yeah. You have to maintain eye contact. Yeah. It's only when you maintain eye contact. [Short phrase unclear.] Yeah. Yeah. Yeah. It is only who you are looking at, then you [rest unclear]. Yeah. Okay. Yeah. That's all for our presentation. Open to Q&A now. [Brief response unclear.]

### 28:55–29:17

[Brief response unclear.] Yeah. Just open to Q&A. Basically, the team looks at [unclear]. The business is challenged, right? So like the earlier team said— [Recording ends mid-sentence.]
