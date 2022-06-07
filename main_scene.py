from manim import *
from manim_speech import VoiceoverScene
from manim_speech.interfaces.gtts import GTTSSpeechSynthesizer
from manim_speech.interfaces.azure import AzureSpeechSynthesizer

GLOBAL_SPEED = 1.05

# SPEECH_SYNTHESIZER = GTTSSpeechSynthesizer()
SPEECH_SYNTHESIZER = AzureSpeechSynthesizer(
    voice="en-US-AriaNeural",
    style="newscast-casual",
    global_speed=GLOBAL_SPEED,
)


class GrowFromSide(Animation):
    def __init__(self, mobject, edge=LEFT, rate_func=smooth, **kwargs):
        self.edge = edge
        if edge[0] != 0:
            self.edge_dim = "width"
        elif edge[1] != 0:
            self.edge_dim = "height"
        super().__init__(mobject, rate_func=rate_func, **kwargs)

    def interpolate_mobject(self, alpha: float):
        self.mobject.become(self.starting_mobject)
        end_val = getattr(self.mobject, self.edge_dim)
        dx = self.rate_func(alpha)
        interpolate_dim = interpolate(0.0001, end_val, dx)
        self.mobject.rescale_to_fit(
            interpolate_dim, self.get_dim(self.edge), stretch=True
        )
        self.mobject.align_to(self.starting_mobject, self.edge)

    def get_dim(self, dim):
        if dim[0] != 0:
            return 0
        return 1


class Wave(VMobject):
    def __init__(self, amp=6, ov=12, num_p=2, l=3, t_offset=0, Dt=0.1, **kwargs):
        def _func(x, t):
            return sum(
                [
                    (amp / ((k + 1) ** 2.5))
                    * np.sin(2 * mult * t)
                    * np.sin(k * mult * x)
                    for k in range(ov)
                    for mult in [(num_p + k) * np.pi]
                ]
            )

        self.func = _func
        self.t_offset = t_offset
        self._l = l
        self._Dt = Dt
        super().__init__(**kwargs)

    def generate_points(self):
        T = np.arange(self.t_offset, self.t_offset + self._l + self._Dt, self._Dt)
        X = np.arange(0, self._l + self._Dt, self._Dt)
        Y = np.array([self.func(x, t) for x, t in zip(X, T)])
        Z = np.zeros(len(Y))
        self.set_points_smoothly(list(zip(X, Y, Z)))


class StyleRectangle(VMobject):
    def __init__(self, mob, sh_1=0.1, sh_2=0.1, v_buff=0.7, h_buff=0.07, **kwargs):
        self.rec = Rectangle(**kwargs).surround(mob, stretch=True, buff=0)
        self.rec.scale([1 + h_buff, 1 + v_buff, 0])
        self.sh_1 = sh_1
        self.sh_2 = sh_2
        super().__init__()

    def generate_points(self):
        curve1 = self.rec.get_subcurve(
            0.25 - self.sh_1, 0.25 + self.sh_2
        ).get_all_points()
        curve2 = self.rec.get_subcurve(
            0.75 - self.sh_1, 0.75 + self.sh_2
        ).get_all_points()
        self.set_points([*curve1, *curve2])


_CODE1 = """class Scene1(MovingCameraScene):
    def construct(self):
        # Create title
        title = VGroup(
            Text("Manim Video Production 101", weight=BOLD),
            Text("Screenplay Writing and Storyboarding", font_size=36),
        ).arrange(DOWN,buff=0.5)
        title.set(width=config.frame_width-1).to_edge(UP)

        self.play(Write(title[0]))
        self.wait()
        self.play(Write(title[1]))
        self.wait()

        # Get screen image
        screen_im = ImageMobject(self.camera.get_image())
        screen_im.width = config.frame_width
        bk = Rectangle().surround(screen_im,buff=0.2,stretch=True)
        bk.set_style(
            fill_opacity=0, stroke_width=10,
            stroke_opacity=1, stroke_color=WHITE
        )
        screen_grp = Group(bk, screen_im)
        # ....
"""


class Scene1(VoiceoverScene, MovingCameraScene):
    def setup(self):
        MovingCameraScene.setup(self)

    def construct(self):
        self.set_speech_synthesizer(SPEECH_SYNTHESIZER)
        self.sub1()
        self.sub2()

    def sub2(self):
        def get_recs(title, color=GREEN):
            t = Tex(title, color=color)
            stroke_rec = Rectangle(
                width=3,
                height=1,
                fill_opacity=0,
                color=color,
                stroke_width=4,
                stroke_color=color,
            )
            stroke_recs = VGroup(*[stroke_rec.copy() for _ in range(3)]).arrange(
                RIGHT, buff=0
            )
            fill_recs = stroke_recs.copy()
            fill_recs.set_style(
                fill_opacity=1, fill_color=color, stroke_width=0, stroke_opacity=0
            )
            t.next_to(stroke_recs, LEFT, buff=0.3)
            line = Line(fill_recs.get_corner(DL), fill_recs.get_corner(DR))
            return line, VGroup(t, stroke_recs, fill_recs)

        vl, video_recs = get_recs("Video", GREEN)
        al, audio_recs = get_recs("Audio", BLUE)

        main_grp = (
            VGroup(video_recs, audio_recs)
            .arrange(DOWN, aligned_edge=RIGHT)
            .shift(UP + LEFT * 0.4)
        )
        al.next_to(audio_recs[1], DOWN, buff=0)
        hours = VGroup(
            *[
                Tex(t).next_to(al.point_from_proportion(0.3333 * i), DOWN)
                for i, t in enumerate(["0:00", "3:00", "9:00", "15:00"])
            ]
        )
        _TEXTS = VGroup(
            Tex(r"Intro\\Scene"),
            Tex(r"Body\\Scene"),
            Tex(r"Conclusion\\Scene"),
        )
        for _t, _r in zip(_TEXTS, audio_recs[1]):
            _t.next_to(_r, DOWN, buff=1.4)
        cross = Cross(_TEXTS[1])

        _anims = [
            GrowFromSide(video_recs[-1][1]),
            GrowFromSide(audio_recs[-1][1]),
            GrowFromSide(audio_recs[-1][0]),
            GrowFromSide(video_recs[-1][0]),
        ]
        with self.voiceover(
            "For example, one could start by animating an idea that belongs in the middle of the video, and then try to come up with an introduction that complements it."
        ) as tk:
            self.play(
                LaggedStart(
                    Write(video_recs[:-1]),
                    Write(audio_recs[:-1]),
                    Write(hours),
                    Write(_TEXTS),
                ),
                run_time=2.5,
            )
            # for _anim in _anims:
            #     self.play(
            #         _anim,
            #         run_time=3
            #     )
            #     self.wait()
            self.play(_anims[0], run_time=1.5)
            self.play(_anims[1], run_time=1.3)
            self.wait(3)
            self.play(_anims[2], run_time=1.2)
            self.wait(0.3)
            self.play(_anims[3], run_time=1.2)
            self.wait(0.5)
        video_recs[-1][1].save_state()
        audio_recs[-1][1].save_state()
        with self.voiceover(
            "Generally, scenes that are created improvisationally end up being modified multiple times or even scrapped, because they don't fit in with the rest."
        ) as tk:
            self.wait(3.2)
            self.play(
                LaggedStart(
                    GrowFromSide(video_recs[-1][1], rate_func=lambda t: smooth(1 - t)),
                    GrowFromSide(audio_recs[-1][1], rate_func=lambda t: smooth(1 - t)),
                    lag_ratio=0.2,
                ),
                run_time=2,
            )
            video_recs[-1][1].restore()
            audio_recs[-1][1].restore()
            self.play(
                LaggedStart(
                    GrowFromSide(video_recs[-1][1]),
                    GrowFromSide(audio_recs[-1][1]),
                    lag_ratio=0.2,
                ),
                run_time=2,
            )
            self.play(
                FadeOut(video_recs[-1][1], shift=UP),
                FadeOut(audio_recs[-1][1], shift=DOWN),
                FadeOut(video_recs[-2][1], shift=UP),
                FadeOut(audio_recs[-2][1], shift=DOWN),
                Create(cross),
            )
        self.wait(0.2)
        with self.voiceover(
            "If you are a beginner to video production, this approach can be highly inefficient, as you might end up wasting a lot of time doing the same scenes again and again. This might be especially discouraging for technical people who aspire to produce videos with Manim."
        ) as tk:
            pass
        with self.voiceover(
            "In this tutorial we seek to alleviate this issue by showing you how to plan out videos in advance."
        ) as tk:
            pass
        self.play(LaggedStartMap(FadeOut, self.mobjects, lag_ratio=0))
        self.wait(0.1)
        # self.add(main_grp)

    def sub1(self):
        title = VGroup(
            Tex("\\bf Manim Video Production 101"),
            Tex("Screenplay Writing and Storyboarding", font_size=36),
        ).arrange(DOWN, buff=0.5)
        title.set(width=config.frame_width - 3).to_edge(UP, buff=1.5)

        def updater_wave(mob, dt):
            t_offset = mob.t_offset + dt * 0.2
            center = mob.get_center()
            width = mob.width
            mob.become(Wave(t_offset=t_offset))
            mob.t_offset = t_offset
            mob.width = width
            mob.move_to(center)

        with self.voiceover(
            text="Welcome to Manim Video Production one-oh-one"
        ) as tracker:
            self.play(Write(title[0]), run_time=tracker.duration)

        with self.voiceover(
            text="""
In this tutorial, we will teach you how to write a screenplay and create a storyboard for your Manim video, so that you can plan things in advance and don't have to re-record or re-animate your scenes.
"""
        ) as tracker:
            self.wait(2.4)
            self.play(Write(title[1]))
        self.wait()

        screen_im = ImageMobject(self.camera.get_image())
        screen_im.width = config.frame_width
        bk = Rectangle().surround(screen_im, buff=0.2, stretch=True)
        bk.set_style(
            fill_opacity=0, stroke_width=10, stroke_opacity=1, stroke_color=WHITE
        )
        screen_grp = Group(bk, screen_im)

        self.add(screen_grp)
        with self.voiceover(
            text="To create a full-fledged Manim video, one needs to come up with multiple layers of media, such as recording voiceovers and implementing the animations in Python."
        ) as tracker:
            self.wait(0.3)
            self.play(
                screen_grp.animate.set(width=3.3)
                .to_corner(DL, buff=1.3)
                .shift(UP * 0.4),
                run_time=3,
            )
            self.wait(2.5)
            code = Code(
                code=_CODE1, language="python", style="monokai", font="Consolas"
            )

            _GRP = (
                Group(
                    MathTex("="),
                    Wave().set(width=screen_grp.width),
                    MathTex("+"),
                    code.set(width=screen_grp.width),
                )
                .arrange(RIGHT)
                .next_to(screen_grp, RIGHT)
            )
            self.play(FadeIn(_GRP[:2]))
            _GRP[1].add_updater(updater_wave)
            self.wait(1)
            self.play(
                Write(_GRP[2]),
                Write(_GRP[3]),
            )
            # self.wait(tracker.duration - 0.3 - 2.4 - 1 - 3.8 - 1.8)

        self.save_screen = ImageMobject(self.camera.get_image())

        bk = Rectangle(width=16, height=9, color=BLACK, fill_opacity=1).set(
            width=config.frame_width
        )
        with self.voiceover(
            "There is more than one way of producing a video. Beginners tend to use an improvisational approach, where one records audio on-the-go and come up with visuals without any specific order or prior planning"
        ) as tk:
            self.wait(tk.duration)
        self.play(FadeIn(bk))
        _GRP[1].clear_updaters()
        self.remove(*self.mobjects)


class Scene2(VoiceoverScene, MovingCameraScene):
    def setup(self):
        MovingCameraScene.setup(self)

    def construct(self):
        self.set_speech_synthesizer(SPEECH_SYNTHESIZER)
        self.sub1()
        self.sub2()

    def sub1(self):
        title = Tex(r"\sf Screenplay", " = ", "Voiceover Text + Verbal Descriptions")
        title.to_edge(UP, buff=1)

        tex_boxes = (
            VGroup(
                *[
                    Tex(t)
                    for t in [
                        "\\sc Introduction",
                        "\\sc Body",
                        "\\sc Conclusion",
                    ]
                ]
            )
            .arrange(DOWN, buff=0.8)
            .to_edge(LEFT, buff=2)
            .shift(UP * 0.7)
        )

        _BOX = StyleRectangle(tex_boxes[0])
        _BOXES = VGroup(*[_BOX.copy().move_to(t) for t in tex_boxes])

        _ZIP = list(zip(tex_boxes, _BOXES))
        _MIDDLE = (
            VGroup(
                Tex("Once upon a time, ..."),
                Tex("This video is about, ..."),
            )
            .arrange(DOWN, buff=0.7, aligned_edge=LEFT)
            .next_to(_BOXES, RIGHT, buff=1)
        )
        _TICK = (
            Text("✓", font="MesloLGS NF", fill_opacity=1, color=GREEN)
            .scale(2)
            .next_to(_MIDDLE[-1], RIGHT)
        )
        _CROSS = Cross(_MIDDLE[0])

        _DOWN = (
            VGroup(
                Tex("Python Script = Single Source of Truth"),
                VGroup(
                    VGroup(Tex("\\sf Essay"), Tex("\\sf Verbal descriptions")).arrange(
                        DOWN
                    ),
                    VGroup(
                        Tex("\\sf Voiceover"), Tex("\\sf Instructions for animation")
                    ).arrange(DOWN),
                ).arrange(RIGHT, buff=2),
            )
            .arrange(DOWN)
            .to_edge(DOWN, buff=1)
        )

        _T_LEFT = _DOWN[1][0]
        _T_RIGHT = _DOWN[1][1]
        p1 = _T_LEFT[1].get_right()
        p2 = _T_RIGHT[1].get_left()
        p2[1] = p1[1]

        _ARROW_DOWN = Arrow(p1, p2)
        _ARROW_UP = _ARROW_DOWN.copy().set_y(_T_RIGHT[0].get_y())

        # self.add(title, tex_boxes, _BOXES)
        with self.voiceover(
            "Most well-produced videos start out their lifetime as a screenplay, which is basically just text. This includes the text of the voiceover to be performed by the narrator and verbal description of the visuals that will constitute the video."
        ) as tk:
            self.wait(3)
            self.play(Write(title[0]))
            self.wait(4.7)
            self.play(Write(title[1:]))

        with self.voiceover(
            "So to produce a video, you first need to write an essay on the topic you are producing about."
        ) as tk:
            self.wait(3)
            self.play(
                LaggedStart(*[LaggedStartMap(Write, _z) for _z in _ZIP], lag_ratio=1),
                run_time=4,
            )

        with self.voiceover("The language does not have to be flowery.") as tk:

            self.play(Write(_MIDDLE[0], run_time=1))
            self.play(Create(_CROSS), run_time=1)

        with self.voiceover(
            "It can be set in a plain and explanatory tone. The main requirement for it is to be coherent and convey information efficiently  about whatever you are trying to explain."
        ) as tk:
            self.play(Write(_MIDDLE[1], run_time=1))
            self.wait()
            self.play(DrawBorderThenFill(_TICK))

        with self.voiceover(
            "Your Python script then acts as a single source of truth when it comes to the latter stages of producing the video."
        ) as tk:
            self.wait()
            self.play(Write(_DOWN[0]))

        with self.voiceover(
            "Your essay becomes the voiceover, and the verbal descriptions remind you or the person responsible for animating how the scene was envisioned at the planning stage."
        ) as tk:
            self.play(Write(_T_LEFT[0]))
            # self.wait(0.5)
            self.play(
                GrowArrow(_ARROW_UP),
                TransformFromCopy(_T_LEFT[0], _T_RIGHT[0]),
                run_time=1,
            )
            # self.wait(0.5)
            self.play(Write(_T_LEFT[1]))
            self.wait(0.5)
            self.play(
                GrowArrow(_ARROW_DOWN),
                TransformFromCopy(_T_LEFT[1], _T_RIGHT[1]),
                run_time=1,
            )

        with self.voiceover(
            "But plain text often falls short in describing visual scenes, especially when it comes to technical subjects. That's why you might need to draw sketches that complement the screenplay. These are simplified drawings or ASCII art that show in sufficient detail how the visuals should come into the scene, move and interact with each other."
        ) as tk:
            self.wait(tk.duration)
        self.play(FadeOut(Group(*self.mobjects), lag_ratio=0))
        self.wait(0.1)

    def sub2(self):
        _UP_TEXT = Tex(
            r"\sf To create a ",
            r"{\tt <Write(1)>}",
            r""" full-fledged Manim video,\\
one needs to come up with multiple layers of media,\\
such as recording """,
            r"{\tt <Write(2)>}",
            r""" voiceovers and\\
implementing the """,
            r"{\tt <Write(3)>}",
            """ animations in Python.""",
            tex_environment="flushleft",
        )
        _UP_TEXT.width = config.frame_width - 3
        _UP_TEXT.to_edge(UP, buff=1)
        _DOWN_TEXT = Paragraph(
            """ [1]  =    [2]     +    [3]
video   recording    manim code

---------------------------

[1] is a window showing the current screen
    (a "rectangle" that contains the everything
    on the screen, one level of depth is enough)
[2] a screen containing the live waveform of the
    audio that is playing at that moment (see below)
[3] is the manim code that generates this scene
""",
            font="Consolas",
            line_spacing=1,
        ).scale(0.29)
        _DOWN_TEXT.to_edge(DOWN, buff=1)
        bk = Rectangle().surround(_DOWN_TEXT, stretch=True, buff=0.6)
        # self.add(_UP_TEXT,_DOWN_TEXT,bk)

        self.wait(0.5)
        with self.voiceover(
            "Let's demonstrate with an earlier scene from this video."
        ) as tk:
            self.wait()
            self.play(Write(_UP_TEXT), run_time=tk.duration - 1)
        self.wait()
        with self.voiceover(
            "As you can see, the screenplay at the top is interleaved with markup that describes exactly when the animations should be triggered. This sort of writing also helps you to imagine the scene before you start writing the code, so that you spend less time redoing things."
        ) as tk:
            self.wait(2.5)
            self.play(Indicate(_UP_TEXT[1]))
            self.play(Indicate(VGroup(*_UP_TEXT[3][:-1], _UP_TEXT[2][-1])))
            self.play(Indicate(VGroup(*_UP_TEXT[5][:-1], _UP_TEXT[4][-1])))

        with self.voiceover(
            "Then you create the storyboard, which is basically a sketch that shows how the objects should look like on the screen."
        ) as tk:
            self.wait()
            self.play(Create(bk), run_time=2)
            self.wait(tk.duration - 1 - 2)

        with self.voiceover(
            "It is divided into top and bottom parts. The top part shows the actual locations and shapes of objects, whereas the bottom part is reserved for comments."
        ) as tk:
            self.wait(1.1)
            self.play(Write(_DOWN_TEXT[:3]), run_time=0.5)
            self.wait(0.2)
            self.play(Write(_DOWN_TEXT[3:]), run_time=0.5)

        with self.voiceover(
            """
        In fact, this entire video has been planned using this special syntax,
        and commissioned to the talented Manim community member Theorem of Beethoven.
        This video proves that it is possible to produce videos efficiently by
        dividing labor between a screenplay writer and a developer, who use
        simple Markdown and drawn sketches to describe how the video should look like.
        """
        ) as tk:
            self.wait(3)
            self.play(FadeOut(Group(*self.mobjects)))
            self.wait(2)
            group1 = VGroup(
                Tex("Theorem of Beethoven", font_size=72),
                Text(
                    "https://www.youtube.com/c/TheoremofBeethoven",
                    font="Consolas",
                    font_size=24,
                ),
            ).arrange(DOWN, buff=0.5)
            self.play(FadeIn(group1))

        self.play(FadeOut(group1))

        with self.voiceover(
            "You can use the link on your screen to access this guide. You can also find it in the video description below."
        ) as tk:
            self.wait(1.2)
            self.play(
                Write(
                    Text(
                        "https://hackmd.io/@prism0x/manim-screenplay-writing-storyboarding",
                        font="Consolas",
                    ).set(width=config.frame_width - 2.5)
                ),
                run_time=1.5,
            )
            self.wait(tk.duration - 1.2 - 1.5)

        self.wait()
        self.play(FadeOut(Group(*self.mobjects)))
        self.wait()
