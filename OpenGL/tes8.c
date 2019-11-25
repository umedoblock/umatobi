/* umatobi simulator
 *
 * Copyright (c) 2012-2019 梅濁酒(=umedoblock)
 *
 * This software is released under the MIT License.
 * https://github.com/umedoblock/umatobi
 */
/* tes8.c
 * Copyright (C) 2008 梅濁酒 umedoblock
 */

#include <GL/gl.h>
#include <GL/glut.h>
#include <stdio.h>
#include <math.h>
#include <time.h>

#define PAI 3.14159265
unsigned int *p;
int num_node;
double key2omega(unsigned int k)
{
    double omega = 0.0, tmp;
    double maxi = 4294967296.0;//(double )(1 << (8*sizeof(unsigned int )));

    tmp = (double )k * (2.0 * PAI / maxi);
    omega = tmp;

    return omega;
}
void key2cs(double *cs, double *sn, unsigned int k)
{
    double omega = key2omega(k);

    *cs =  cos(omega + (3.0 * PAI / 2.0 )) * 0.99;
    *sn = -sin(omega + (3.0 * PAI / 2.0 )) * 0.99;
}
int ww, hh;
void display(void)
{
    int i, j, n=num_node;
    unsigned int s;
    double dx, dy, dxx, dyy, px, py, t, step;
    clock_t start, end;
    static double flame = 0.0, sec = 0.0;
    double fps;

    glClearColor(0, 0, 0, 0);
    glClear(GL_COLOR_BUFFER_BIT);

    start = clock();
    //点を描画していく
    glPointSize(4.0);
    glBegin(GL_QUADS);
    for(i=0;i<n;i++){
        //色の設定
        glColor3f((i+3)%3==0, (i+2)%3==0, (i+1)%3==0);

        step = 0.02;
        //自分の位置を確認
        key2cs(&dx, &dy, p[i]);
        glVertex2d(dx,      dy);
        glVertex2d(dx,      dy-step);
        glVertex2d(dx+step, dy-step);
        glVertex2d(dx+step, dy);
    }
    glEnd();

    //線を引くための前準備
    glEnable(GL_LINE_STIPPLE);
    glLineStipple(1, 0xf0f0);

    //線を結んでいく
    glBegin(GL_LINES);
    for(i=0;i<n;i++){
        //色の設定
        glColor3f((i+3)%3==0, (i+2)%3==0, (i+1)%3==0);

        //自分の位置を確認
        key2cs(&dx, &dy, p[i]);
        glVertex2d(dx, dy);

        //相手の位置を確認
        key2cs(&dxx, &dyy, p[n-i-1]);
        //自分と相手の中間の位置を計算
        px = (dx + dxx) / 2.0;
        py = (dy + dyy) / 2.0;

        //自分と相手の中間まで直線を引く
        glVertex2d(px, py);
    }
    glEnd();

    glFinish();
    end = clock();

    t = (double)(end - start) / CLOCKS_PER_SEC;
    sec += t;
    flame += 1.0;
    fps = flame / sec;

    fprintf(stdout, "t=%lf, flame = %lf, sec = %lf\n", t, flame, sec);
    fprintf(stdout, "fps=%lf\n", fps);
}
int main(int argc , char *argv[])
{
    int width, height, pixel;
    int i;
    if (argc >= 3){
        pixel = atoi(argv[1]);
        num_node = atoi(argv[2]);
    }else{
        pixel = 500;
        num_node = 1024;
    }
    fprintf(stdout, "pixel=%d, node=%d\n", pixel, num_node);
    srand(time(NULL));
    p = (unsigned int *)malloc(sizeof(unsigned int) * num_node);
    if(p == NULL){
        fprintf(stderr, "malloc(%d) failed\n", sizeof(unsigned int) * num_node);
        exit(1);
    }
    for(i=0;i<num_node;i++){
        p[i] = (rand() << 16) + rand() + (rand() << 31);
    }

    ww = hh = width = height = pixel;

    glutInit(&argc , argv);
    glutInitWindowPosition(0, 0);
    glutInitWindowSize(width, height);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA);

    glutCreateWindow(argv[0]);
    glutDisplayFunc(display);

    glutMainLoop();

    free(p);
    return 0;
}
