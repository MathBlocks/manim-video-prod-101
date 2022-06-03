from manim import *

class GrowFromSide(Animation):
    def __init__(self, mobject, edge=LEFT, rate_func=smooth,**kwargs):
        self.edge = edge
        if edge[0] != 0:
            self.edge_dim = "width"
        elif edge[1] != 0:
            self.edge_dim = "height"
        super().__init__(mobject, rate_func=rate_func, **kwargs)

    def interpolate_mobject(self, alpha: float):
        self.mobject.become(self.starting_mobject)
        end_val = getattr(self.mobject,self.edge_dim)
        dx = self.rate_func(alpha)
        interpolate_dim = interpolate(0.0001,end_val,dx)
        self.mobject.rescale_to_fit(interpolate_dim, self.get_dim(self.edge), stretch=True)
        self.mobject.align_to(self.starting_mobject,self.edge)

    def get_dim(self, dim):
        if dim[0] != 0:
            return 0
        return 1

class Wave(VMobject):
    def __init__(self, amp=6, ov=12, num_p=2, l=3, t_offset=0, Dt=0.1, **kwargs):
        def _func(x, t):
            return sum([
                (amp/((k+1)**2.5))*np.sin(2*mult*t)*np.sin(k*mult*x)
                for k in range(ov)
                for mult in [(num_p+k)*np.pi]
            ])
        self.func = _func
        self.t_offset = t_offset
        self._l = l
        self._Dt = Dt
        super().__init__(**kwargs)

    def generate_points(self):
        T = np.arange(self.t_offset, self.t_offset + self._l + self._Dt, self._Dt)
        X = np.arange(0, self._l + self._Dt, self._Dt)
        Y = np.array([self.func(x, t) for x,t in zip(X,T)])
        Z = np.zeros(len(Y))
        self.set_points_smoothly(list(zip(X,Y,Z)))

class StyleRectangle(VMobject):
    def __init__(self, mob, sh_1=0.1, sh_2=0.1, v_buff=0.7, h_buff=0.07,**kwargs):
        self.rec = Rectangle(**kwargs).surround(mob, stretch=True, buff=0)
        self.rec.scale([1+h_buff,1+v_buff,0])
        self.sh_1 = sh_1
        self.sh_2 = sh_2
        super().__init__()

    def generate_points(self):
        curve1 = self.rec.get_subcurve(0.25-self.sh_1,0.25+self.sh_2).get_all_points()
        curve2 = self.rec.get_subcurve(0.75-self.sh_1,0.75+self.sh_2).get_all_points()
        self.set_points([
            *curve1, *curve2
        ])

_CODE1 = '''class Scene1(MovingCameraScene):
    def construct(self):
        # Create title
        title = VGroup(
            Text("Manim Video Production 101", weight=BOLD),
            Text("Scripting and Storyboarding"),
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
'''


class Scene1(MovingCameraScene):
    def construct(self):
        self.sub1()
        self.sub2()

    def sub2(self):
        def get_recs(title, color=GREEN):
            t = Text(title,color=color)
            stroke_rec = Rectangle(
                width=3.5,height=1.3,
                fill_opacity=0,color=color,
                stroke_width=4,stroke_color=color
            )
            stroke_recs = VGroup(*[stroke_rec.copy() for _ in range(3)])\
                .arrange(RIGHT,buff=0)
            fill_recs = stroke_recs.copy()
            fill_recs.set_style(
                fill_opacity=1,
                fill_color=color,
                stroke_width=0,
                stroke_opacity=0
            )
            t.next_to(stroke_recs,LEFT,buff=0.3)
            line = Line(fill_recs.get_corner(DL),fill_recs.get_corner(DR))
            return line, VGroup(t, stroke_recs, fill_recs)

        vl, video_recs = get_recs("Video", GREEN)
        al, audio_recs = get_recs("Audio", BLUE)

        main_grp = VGroup(video_recs, audio_recs).arrange(DOWN, aligned_edge=RIGHT).shift(UP)
        al.next_to(audio_recs[1],DOWN,buff=0)
        hours = VGroup(*[
            Text(t).next_to(al.point_from_proportion(0.3333*i), DOWN)
            for i,t in enumerate(["0:00","3:00","9:00","15:00"])
        ])
        _TEXTS = VGroup(
            Tex(r"Intro\\Scene"),
            Tex(r"Body\\Scene"),
            Tex(r"Conclusion\\Scene"),
        )
        for _t,_r in zip(_TEXTS, audio_recs[1]): _t.next_to(_r,DOWN,buff=1.4)
        cross = Cross(_TEXTS[1])

        _anims = [
            GrowFromSide(video_recs[-1][1]),
            GrowFromSide(audio_recs[-1][1]),
            GrowFromSide(audio_recs[-1][0]),
            GrowFromSide(video_recs[-1][0]),
        ]

        self.play(
            LaggedStart(
                Write(video_recs[:-1]),
                Write(audio_recs[:-1]),
                Write(hours),
                Write(_TEXTS),
            )
        )
        self.wait()
        for _anim in _anims:
            self.play(
                _anim,
                run_time=3
            )
            self.wait()
        video_recs[-1][1].save_state()
        audio_recs[-1][1].save_state()
        self.play(
            LaggedStart(
                GrowFromSide(video_recs[-1][1],rate_func=lambda t: smooth(1-t)),
                GrowFromSide(audio_recs[-1][1],rate_func=lambda t: smooth(1-t)),
                lag_ratio=0.2
            ),
            run_time=2
        )
        video_recs[-1][1].restore()
        audio_recs[-1][1].restore()
        self.play(
            LaggedStart(
                GrowFromSide(video_recs[-1][1]),
                GrowFromSide(audio_recs[-1][1]),
                lag_ratio=0.2
            ),
            run_time=2
        )
        self.play(
            FadeOut(video_recs[-1][1],shift=UP),
            FadeOut(audio_recs[-1][1],shift=DOWN),
            FadeOut(video_recs[-2][1],shift=UP),
            FadeOut(audio_recs[-2][1],shift=DOWN),
            Create(cross)
        )
        self.wait()
        self.play(
            LaggedStartMap(FadeOut,self.mobjects,lag_ratio=0)
        )
        self.wait(0.1)
        # self.add(main_grp)

    
    def sub1(self):
        title = VGroup(
            Text("Manim Video Production 101", weight=BOLD),
            Text("Scripting and Storyboarding"),
        ).arrange(DOWN,buff=0.5)
        title.set(width=config.frame_width-1).to_edge(UP)

        self.play(Write(title[0]))
        self.wait()
        self.play(Write(title[1]))
        self.wait()

        screen_im = ImageMobject(self.camera.get_image())
        screen_im.width = config.frame_width
        bk = Rectangle().surround(screen_im,buff=0.2,stretch=True)
        bk.set_style(
            fill_opacity=0, stroke_width=10,
            stroke_opacity=1, stroke_color=WHITE
        )
        screen_grp = Group(bk, screen_im)

        self.add(screen_grp)
        self.wait()
        self.play(
            screen_grp.animate
                .set(width=3.3)
                .to_corner(DL,buff=1.3)
                .shift(UP*0.4),
            run_time=3
        )
        self.wait()

        code = Code(
            code=_CODE1,
            language="python",
            style="monokai",
            font="Fira Code"
        )

        _GRP = Group(
            MathTex("="),
            Wave().set(width=screen_grp.width),
            MathTex("+"),
            code.set(width=screen_grp.width)
        ).arrange(RIGHT).next_to(screen_grp, RIGHT)

        def updater_wave(mob, dt):
            t_offset = mob.t_offset + dt * 0.2
            center = mob.get_center()
            width = mob.width
            mob.become(Wave(t_offset=t_offset))
            mob.t_offset = t_offset
            mob.width = width
            mob.move_to(center)

        self.play(
            FadeIn(_GRP[:2])
        )
        self.wait()
        _GRP[1].add_updater(updater_wave)    
        self.wait()
        self.play(
            Write(_GRP[2]),
            Write(_GRP[3]),
        )
        self.wait(3)

        self.save_screen = ImageMobject(self.camera.get_image())

        bk = Rectangle(
            width=16,height=9,
            color=BLACK,fill_opacity=1
        ).set(width=config.frame_width)
        self.play(FadeIn(bk))
        _GRP[1].clear_updaters()
        self.remove(*self.mobjects)


class Scene2(Scene):
    def construct(self):
        self.sub1()
        self.sub2()

    def sub1(self):
        title = Tex(r"\sf Script"," = ","Voiceover Text + Verbal Descriptions")
        title.to_edge(UP)

        tex_boxes = VGroup(*[
            Tex(t)
            for t in [
                "\\sc Introduction",
                "\\sc Body",
                "\\sc Conclusion",
            ]
        ]).arrange(DOWN,buff=0.8).to_edge(LEFT,buff=2).shift(UP)

        _BOX = StyleRectangle(tex_boxes[0])
        _BOXES = VGroup(*[
            _BOX.copy().move_to(t)
            for t in tex_boxes
        ])

        _ZIP = list(zip(tex_boxes,_BOXES))
        _MIDDLE = VGroup(
            Tex("Once upon a time, ..."),
            Tex("This video is about, ..."),
        ).arrange(DOWN,buff=0.7,aligned_edge=LEFT).next_to(_BOXES,RIGHT,buff=1)
        _TICK = Text(
            "✓",font="MesloLGS NF",
            fill_opacity=1,
            color=GREEN
        ).scale(2).next_to(_MIDDLE[-1],RIGHT)
        _CROSS = Cross(_MIDDLE[0])

        _DOWN = VGroup(
            Tex("Single Source of Truth"),
            VGroup(
                VGroup(Tex("\\sf Essay"),Tex("\\sf Verbal descriptions")).arrange(DOWN),
                VGroup(Tex("\\sf Voiceover"),Tex("\\sf Instructions for animation")).arrange(DOWN)
            ).arrange(RIGHT,buff=2),
        ).arrange(DOWN).to_edge(DOWN,buff=1)

        _T_LEFT = _DOWN[1][0]
        _T_RIGHT = _DOWN[1][1]
        _ARROW_DOWN = Arrow(_T_LEFT[1].get_right(),_T_RIGHT[1].get_left())
        _ARROW_UP = _ARROW_DOWN.copy().set_y(_T_RIGHT[0].get_y())

        # self.add(title, tex_boxes, _BOXES)
        self.play(Write(title[0]))
        self.wait()
        self.play(Write(title[1:]))
        self.wait()

        self.play(
            LaggedStart(*[
                LaggedStartMap(Write,_z)
                for _z in _ZIP
            ],lag_ratio=1)
        )
        self.wait()

        self.play(
            Write(_MIDDLE[0])
        )
        self.wait()
        self.play(
            Write(_MIDDLE[1])
        )
        self.wait()
        self.play(
            Create(_CROSS)
        )
        self.wait()
        self.play(
            DrawBorderThenFill(_TICK)
        )
        self.wait()
        self.play(Write(_DOWN[0]))
        self.wait()
        self.play(Write(_T_LEFT[0]))
        self.wait()
        self.play(
            GrowArrow(_ARROW_UP),
            TransformFromCopy(_T_LEFT[0],_T_RIGHT[0]),
            run_time=3
        )
        self.wait()
        self.play(Write(_T_LEFT[1]))
        self.wait()
        self.play(
            GrowArrow(_ARROW_DOWN),
            TransformFromCopy(_T_LEFT[1],_T_RIGHT[1]),
            run_time=3
        )
        self.wait(2)
        self.play(FadeOut(Group(*self.mobjects),lag_ratio=0))
        self.wait(0.1)

    def sub2(self):
        _UP_TEXT = Tex(r'\sf To create a ',r'{\tt <Write(1)>}',r''' full-fledged Manim video,\\
one needs to come up with multiple layers of media,\\
such as recording ''',r'{\tt <Write(2)>}',r''' voiceovers and\\
implementing the ''',r'{\tt <Write(3)>}',''' animations in Python.''',tex_environment="flushleft")
        _UP_TEXT.width = config.frame_width - 3
        _UP_TEXT.to_edge(UP)
        _DOWN_TEXT = Paragraph(""" [1]  =    [2]     +    [3]
video   recording    manim code

- - - - - - - - - - - - - - - - - - - - - - - - - -

[1] is a window showing the current screen 
    (a "rectangle" that contains the everything 
    on the screen, one level of depth is enough)
[2] a screen containing the live waveform of the 
    audio that is playing at that moment (see below)
[3] is the manim code that generates this scene
""", font="Fira Code",line_spacing=1).scale(0.34)
        _DOWN_TEXT.to_edge(DOWN,buff=0.7)
        bk = Rectangle().surround(_DOWN_TEXT,stretch=True,buff=0.6)
        # self.add(_UP_TEXT,_DOWN_TEXT,bk)
        self.play(
            Write(_UP_TEXT),run_time=6
        )
        self.wait()

        self.play(Indicate(_UP_TEXT[1]))
        self.play(Indicate(VGroup(*_UP_TEXT[3][:-1],_UP_TEXT[2][-1])))
        self.play(Indicate(VGroup(*_UP_TEXT[5][:-1],_UP_TEXT[4][-1])))
        self.wait()
        self.play(Write(_DOWN_TEXT),Create(bk))
        self.wait(3)
